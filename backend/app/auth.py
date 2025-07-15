import os, json, datetime as _dt
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import ChannelCredentials
from dotenv import load_dotenv

load_dotenv(".env")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
]

CLIENT_SECRETS_FILE = "client_secret.json"
REDIRECT_URI        = os.getenv("REDIRECT_URI", "http://localhost:8000/oauth2callback")

def get_flow():
    return Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

# ---------- DB helpers ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_credentials(channel_id: str, creds: Credentials, db: Session):
    row = (
        db.query(ChannelCredentials)
        .filter(ChannelCredentials.channel_id == channel_id)
        .first()
    )
    if not row:
        row = ChannelCredentials(channel_id=channel_id)
    row.refresh_token = creds.refresh_token
    row.client_id     = creds.client_id
    row.client_secret = creds.client_secret
    row.scopes        = " ".join(creds.scopes)
    row.expiry        = creds.expiry

    db.add(row)
    db.commit()

def load_credentials(channel_id: str, db: Session) -> Credentials | None:
    row = (
        db.query(ChannelCredentials)
        .filter(ChannelCredentials.channel_id == channel_id)
        .first()
    )
    if not row:
        return None
    return Credentials(
        None,
        refresh_token=row.refresh_token,
        token_uri=row.token_uri,
        client_id=row.client_id,
        client_secret=row.client_secret,
        scopes=row.scopes.split(),
    ) 