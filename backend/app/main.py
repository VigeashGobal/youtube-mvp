import os, json, requests
from fastapi import FastAPI, Depends, Response, Request as FastAPIRequest
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest
from google_auth_oauthlib.flow import Flow
from .auth import get_flow, save_credentials, get_db
from .models import ChannelCredentials, Base
from .db import engine
from sqlalchemy.orm import Session
# Public analysis import
from .public_analysis import get_channel_report

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Creator Funding API")

# Mount static files - adjust path for Vercel
static_dir = "public" if os.path.exists("public") else "../public"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates - adjust path for Vercel
templates_dir = "public" if os.path.exists("public") else "../public"
templates = Jinja2Templates(directory=templates_dir)

@app.get("/")
def dashboard(request: FastAPIRequest):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/test")
def test_endpoint():
    """Test endpoint for Vercel debugging"""
    return {"message": "API is working!", "status": "success"}

@app.get("/login")
def login():
    flow = get_flow()
    auth_uri, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return RedirectResponse(auth_uri)

@app.get("/oauth2callback")
def oauth2callback(code: str, db: Session = Depends(get_db)):
    flow = get_flow()
    flow.fetch_token(code=code)

    creds = flow.credentials
    youtube = build("youtube", "v3", credentials=creds)
    channel_resp = (
        youtube.channels()
        .list(part="id", mine=True)
        .execute()
    )
    channel_id = channel_resp["items"][0]["id"]

    save_credentials(channel_id, creds, db)

    return HTMLResponse(
        f"<h3>✅ Connected channel {channel_id}</h3>"
        "<p>You may close this tab and return to the dashboard.</p>"
    )

# ---------- Public-URL lookup ----------
@app.get("/public/analyze")
def public_analyze(url: str, days: int = 30):
    """
    Paste any YouTube channel URL/handle/name → get public stats,
    GPT-generated summary, and an estimated advance.
    """
    try:
        return get_channel_report(url, days)
    except Exception as e:
        return {"error": str(e)}

# ---------- Dashboard API endpoints ----------
@app.get("/api/channels")
def get_connected_channels(db: Session = Depends(get_db)):
    """Get all connected channels"""
    channels = db.query(ChannelCredentials).all()
    return [{"channel_id": c.channel_id} for c in channels]

@app.get("/api/analyze")
def analyze_channel(url: str, days: int = 30):
    """Analyze a channel via URL"""
    try:
        return get_channel_report(url, days)
    except Exception as e:
        return {"error": str(e)} 