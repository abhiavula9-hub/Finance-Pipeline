"""
api/server.py
FastAPI server — exposes the pipeline as a REST endpoint.
Clients (or the dashboard) POST a CSV file and get back the full analysis.

Endpoints:
  POST /analyze   — accepts multipart CSV upload, returns JSON report
  GET  /health    — simple liveness check
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents.supervisor import run_supervisor
from core.config import APP_TITLE, APP_VERSION

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# Allow the Streamlit dashboard (running on another port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Quick check to confirm the server is running."""
    return {"status": "ok", "version": APP_VERSION}


@app.post("/analyze")
async def analyze_transactions(file: UploadFile = File(...)):
    """
    Accept a CSV upload and run the full multi-agent pipeline.
    Returns the complete analysis as JSON.
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    try:
        csv_bytes   = await file.read()
        csv_content = csv_bytes.decode("utf-8")

        # Hand off to the Supervisor, which orchestrates all agents
        result = run_supervisor(csv_content)
        return {"status": "success", "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
