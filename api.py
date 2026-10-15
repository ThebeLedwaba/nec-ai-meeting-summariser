
"""
NEC AI Meeting Summariser - FastAPI Backend
Exposes the pipeline as an HTTP API.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import sqlite3
from pipeline import process_meeting, DB_PATH

app = FastAPI(
    title="NEC AI Meeting Summariser",
    description="Local AI pipeline for meeting transcription and summarisation",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "service": "NEC AI Meeting Summariser",
        "version": "1.0.0",
        "endpoints": ["/process", "/meetings", "/health"]
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/process")
async def process(audio: UploadFile = File(...)):
    """Accept an audio file and return a summary with action items."""
    # Validate file type
    allowed = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}
    ext = os.path.splitext(audio.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {allowed}"
        )

    # Save uploaded file to a temp location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {e}")

    # Run the pipeline
    try:
        result = process_meeting(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return JSONResponse({
        "status": "success",
        "audio_filename": audio.filename,
        "duration_seconds": result["duration"],
        "transcript": result["transcript"],
        "summary": result["summary"]
    })


@app.get("/meetings")
def list_meetings(limit: int = 10):
    """Return the most recent meetings from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, timestamp, audio_filename, duration_seconds, summary "
        "FROM meetings ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()

    return {
        "count": len(rows),
        "meetings": [
            {
                "id": r[0],
                "timestamp": r[1],
                "audio_filename": r[2],
                "duration_seconds": r[3],
                "summary": r[4]
            }
            for r in rows
        ]
    }
