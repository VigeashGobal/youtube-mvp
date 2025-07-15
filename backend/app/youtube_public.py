import os, re, datetime as _dt
from typing import Dict
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv(".env")
API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise EnvironmentError("Add YOUTUBE_API_KEY to your .env")

yt = build("youtube", "v3", developerKey=API_KEY)

def _search_channel(q: str) -> str | None:
    resp = yt.search().list(part="snippet", q=q, type="channel", maxResults=1).execute()
    if resp["items"]:
        return resp["items"][0]["snippet"]["channelId"]
    return None

def resolve_channel_id(text: str) -> str:
    """Accepts URL, @handle, or plain name – returns UC-id."""
    text = text.strip()
    # 1) UC…
    m = re.search(r"(UC[0-9A-Za-z_-]{22})", text)
    if m:
        return m.group(1)
    # 2) @handle
    m = re.search(r"@([A-Za-z0-9_\-.]+)", text)
    if m and (cid := _search_channel(f"@{m.group(1)}")):
        return cid
    # 3) fallback search
    cid = _search_channel(text)
    if cid:
        return cid
    raise ValueError("Could not resolve channel ID.")

def fetch_public_metrics(channel_id: str, days: int = 30) -> Dict[str, int]:
    """Returns subs, total views, video count, recent views."""
    c = yt.channels().list(id=channel_id, part="statistics,contentDetails").execute()
    if not c["items"]:
        raise ValueError("Channel not found.")
    s  = c["items"][0]["statistics"]
    pl = c["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    vids = yt.playlistItems().list(playlistId=pl, part="snippet", maxResults=50).execute()
    ids  = [v["snippet"]["resourceId"]["videoId"] for v in vids["items"]]
    cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=days)
    recent = 0
    if ids:
        chunks = [ids[i:i+50] for i in range(0, len(ids), 50)]
        for ch in chunks:
            v = yt.videos().list(id=",".join(ch), part="statistics,snippet").execute()
            for it in v["items"]:
                views = int(it["statistics"].get("viewCount", 0))
                pub   = _dt.datetime.fromisoformat(it["snippet"]["publishedAt"].replace("Z","+00:00"))
                if pub >= cutoff.replace(tzinfo=_dt.timezone.utc):
                    recent += views
    return {
        "subscriber_count": int(s.get("subscriberCount", 0)),
        "total_views": int(s.get("viewCount", 0)),
        f"views_last_{days}d": recent,
        "video_count": int(s.get("videoCount", 0)),
    } 