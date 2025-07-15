from sqlalchemy import (
    Column, String, Integer, Float, Date, DateTime, UniqueConstraint
)
from .db import Base

class ChannelCredentials(Base):
    __tablename__ = "channel_credentials"
    id            = Column(Integer, primary_key=True, index=True)
    channel_id    = Column(String, unique=True, index=True, nullable=False)
    refresh_token = Column(String, nullable=False)
    token_uri     = Column(String, default="https://oauth2.googleapis.com/token")
    client_id     = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)
    scopes        = Column(String, nullable=False)
    expiry        = Column(DateTime, nullable=True)

class ChannelDailyStats(Base):
    __tablename__ = "channel_daily_stats"
    id              = Column(Integer, primary_key=True, index=True)
    channel_id      = Column(String, index=True, nullable=False)
    date            = Column(Date,  index=True, nullable=False)
    views           = Column(Integer)
    minutes_watched = Column(Integer)
    revenue         = Column(Float)
    subs_gained     = Column(Integer)
    subs_lost       = Column(Integer)

    __table_args__ = (
        UniqueConstraint("channel_id", "date", name="_channel_date_uc"),
    ) 