from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

app = FastAPI()

@app.get("/api/analyze")
def analyze_channel(url: str, days: int = 30):
    try:
        from app.public_analysis import get_channel_report
        return get_channel_report(url, days)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Analysis failed",
                "message": str(e),
                "url": url,
                "days": days
            }
        )

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "youtube_configured": bool(os.getenv("YOUTUBE_API_KEY"))
    }

@app.get("/test")
def test_endpoint():
    return {"message": "API is working!", "status": "success"}

# Export for Vercel
handler = app 