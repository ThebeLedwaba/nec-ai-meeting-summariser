
"""
NEC AI Meeting Summariser - Core Pipeline
Transcribes audio and generates a summary with action items.
Logs every summary to a SQLite database.
"""

import requests
import sqlite3
from datetime import datetime
from pathlib import Path


DB_PATH = "meetings.db"


def init_db():
    """Create the meetings table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            audio_filename TEXT,
            duration_seconds REAL,
            transcript TEXT,
            summary TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_meeting(audio_filename, duration, transcript, summary):
    """Save a summarised meeting to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meetings (timestamp, audio_filename, duration_seconds, transcript, summary)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        audio_filename,
        duration,
        transcript,
        summary
    ))
    conn.commit()
    conn.close()


def transcribe_audio(audio_path, model_size="base.en"):
    """Transcribe audio file to text using faster-whisper."""
    from faster_whisper import WhisperModel
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, beam_size=5)
    text = " ".join([seg.text for seg in segments]).strip()
    return text, info.duration


def generate_summary(transcript, model="llama3.2:3b"):
    """Generate summary and action items from transcript using Ollama."""
    prompt = f"""You are a meeting summariser. Given the following transcript, produce:
1. A short summary (2-3 sentences)
2. A list of action items with owners where stated

Transcript:
"{transcript}"

Output format:
SUMMARY:
<summary>

ACTION ITEMS:
- <item> - <owner>
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=300
    )
    return response.json()["response"]


def process_meeting(audio_path):
    """Full pipeline: audio file to summary with logging."""
    print("Transcribing...")
    transcript, duration = transcribe_audio(audio_path)

    print("Summarising...")
    summary = generate_summary(transcript)

    print("Logging to database...")
    log_meeting(
        audio_filename=Path(audio_path).name,
        duration=duration,
        transcript=transcript,
        summary=summary
    )

    return {
        "transcript": transcript,
        "summary": summary,
        "duration": duration
    }


# Initialise the database on import
init_db()


if __name__ == "__main__":
    result = process_meeting("test_meeting.mp3")
    print("=" * 60)
    print("TRANSCRIPT:")
    print(result["transcript"])
    print("=" * 60)
    print("SUMMARY:")
    print(result["summary"])
