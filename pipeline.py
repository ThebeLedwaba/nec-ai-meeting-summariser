
"""
NEC AI Meeting Summariser - Core Pipeline
Transcribes audio, generates summary with action items, logs to SQLite,
and notifies n8n webhook for Slack delivery.
"""

import requests
import sqlite3
import os
from datetime import datetime
from pathlib import Path


DB_PATH = "meetings.db"
N8N_WEBHOOK_URL = "https://pound-pty-compatibility-decor.trycloudflare.com/webhook/meeting-processed"


def init_db():
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


def notify_n8n(audio_filename, duration, summary):
    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json={
                "audio_filename": audio_filename,
                "duration_seconds": duration,
                "summary": summary
            },
            timeout=15
        )
        print(f"n8n notified: {response.status_code}")
    except Exception as e:
        print(f"n8n notification error: {e}")


def transcribe_audio(audio_path, model_size="base.en"):
    from faster_whisper import WhisperModel
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, beam_size=5)
    text = " ".join([seg.text for seg in segments]).strip()
    return text, info.duration


def generate_summary(transcript, model="llama3.2:3b"):
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

    print("Notifying n8n...")
    notify_n8n(
        audio_filename=Path(audio_path).name,
        duration=duration,
        summary=summary
    )

    return {
        "transcript": transcript,
        "summary": summary,
        "duration": duration
    }


init_db()


if __name__ == "__main__":
    result = process_meeting("test_meeting.mp3")
    print("=" * 60)
    print(result["summary"])
