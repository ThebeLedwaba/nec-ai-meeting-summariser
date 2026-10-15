# NEC AI Meeting Summariser

A local AI pipeline that transcribes meeting audio, generates a summary with action items, and logs every meeting to a local database.

## Features

- Offline transcription using faster-whisper
- Local LLM summarisation using Ollama (Llama 3.2)
- Action-item extraction with owner attribution
- SQLite logging of every summarised meeting
- FastAPI backend exposing the pipeline over HTTP

## Architecture

Audio file -> faster-whisper -> transcript
    -> Ollama (Llama 3.2 3B) -> summary + action items
    -> SQLite database -> FastAPI

## Tech Stack

| Layer | Tool |
|-------|------|
| Transcription | faster-whisper (base.en, CPU int8) |
| Summarisation | Ollama + Llama 3.2 3B |
| Database | SQLite |
| Backend | FastAPI + Uvicorn |

## Files

- pipeline.py - core transcription + summarisation pipeline
- api.py - FastAPI backend with /process, /meetings, /health endpoints
- meetings.db - SQLite database of past meetings

## Setup

### Prerequisites

- Python 3.11+
- Ollama installed (ollama.com)
- At least 8 GB RAM

### Install

pip install faster-whisper fastapi uvicorn python-multipart
ollama pull llama3.2:3b

### Run

uvicorn api:app --host 0.0.0.0 --port 8000

### Test

curl http://localhost:8000/health
curl -X POST http://localhost:8000/process -F "audio=@test_meeting.mp3"

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | / | Service info |
| GET | /health | Health check |
| POST | /process | Upload audio, get summary |
| GET | /meetings | Retrieve meeting history |

## Status

- Backend: complete
- Streamlit UI: in progress
- n8n workflow: pending

## Author

Thebe Ledwaba - EINTP4A Capstone Project, VUT 2026
