import sys
import os

# Add the backend directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, '..', 'backend')
sys.path.insert(0, backend_path)

try:
    # Import the FastAPI app
    from app.main import app
    
    # Export the app for Vercel
    handler = app
    
except Exception as e:
    # Create a simple error handler if import fails
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/api/analyze")
    def analyze_channel(url: str, days: int = 30):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Server configuration error",
                "message": f"Failed to import main application: {str(e)}",
                "details": "Please check the server logs for more information."
            }
        )
    
    @app.get("/health")
    def health_check():
        return {
            "status": "error",
            "message": f"Import failed: {str(e)}",
            "import_error": True
        }
    
    @app.get("/test")
    def test_endpoint():
        return {
            "message": "API is working but with import error",
            "error": str(e)
        }
    
    handler = app 