"""
Run with:  PYTHONPATH=./backend python backend/app/jobs.py
It will pull the last-30-days stats for every connected channel once a day.
"""
import datetime as _dt
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from apscheduler.schedulers.blocking import BlockingScheduler
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from sqlalchemy.orm import Session

from app.db import SessionLocal, engine
from app.models import Base, ChannelCredentials, ChannelDailyStats
from app.auth import load_credentials

Base.metadata.create_all(bind=engine)

METRICS = (
    "views"
)

def fetch_all_time_stats(db: Session, channel_id: str, creds):
    yt = build("youtubeAnalytics", "v2", credentials=creds)
    end   = _dt.date.today()
    start = _dt.date(2010, 1, 1)  # YouTube Analytics started around 2010

    resp = yt.reports().query(
        ids=f"channel=={channel_id}",
        startDate=start.isoformat(),
        endDate=end.isoformat(),
        dimensions="day",
        metrics=METRICS,
    ).execute()

    import pprint
    print(f"\n📊 FULL API RESPONSE for {channel_id}:")
    pprint.pprint(resp)
    print(f"   Rows returned: {len(resp.get('rows', []))}")
    print(f"   Response keys: {list(resp.keys())}")
    if 'rows' in resp and resp['rows']:
        print(f"   Sample row: {resp['rows'][0]}")
    else:
        print(f"   No rows returned")

    for row in resp.get("rows", []):
        date_str, views = row
        date = _dt.date.fromisoformat(date_str)

        stat = (
            db.query(ChannelDailyStats)
              .filter_by(channel_id=channel_id, date=date)
              .first()
        ) or ChannelDailyStats(channel_id=channel_id, date=date)

        stat.views           = int(views)
        stat.minutes_watched = 0
        stat.revenue         = 0.0
        stat.subs_gained     = 0
        stat.subs_lost       = 0

        db.add(stat)
    db.commit()

def daily_job():
    db = SessionLocal()
    for row in db.query(ChannelCredentials).all():
        creds = load_credentials(row.channel_id, db)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            db.commit()
        fetch_all_time_stats(db, row.channel_id, creds)
    db.close()
    print(f"✅  Ingest finished at {_dt.datetime.utcnow():%Y-%m-%d %H:%M}Z")

if __name__ == "__main__":
    sched = BlockingScheduler(timezone="UTC")
    # run immediately on startup, then every 24 h
    sched.add_job(daily_job, "interval", days=1, next_run_time=_dt.datetime.utcnow())
    print("⏰  Scheduler started – pulling all-time YouTube Analytics every 24 h")
    sched.start() 