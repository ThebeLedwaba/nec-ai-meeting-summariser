# NEC AI Meeting Summariser

A fully offline AI pipeline that transcribes meeting audio, generates a summary with action items, logs every meeting to a local database, and automatically delivers the report via Slack.

## Features

- Offline Transcription: Using faster-whisper (base.en model).
- Local LLM Summarisation: Using Ollama (Llama 3.2 3B).
- Action-Item Extraction: Automatically identifies tasks and owners.
- Automated Delivery: Self-hosted n8n webhook pushes the summary to Slack.
- SQLite Logging: Keeps a local history of every summarised meeting.
- Cloud Frontend: Streamlit interface deployed to Streamlit Community Cloud.
- FastAPI Backend: Exposes the pipeline over HTTP.

## Architecture

Audio file -> Streamlit UI -> FastAPI -> faster-whisper -> transcript
    -> Ollama (Llama 3.2 3B) -> summary + action items
    -> SQLite database & n8n Webhook -> Slack

## Tech Stack

| Layer | Tool |
|-------|------|
| Frontend UI | Streamlit (Deployed on Streamlit Cloud) |
| Transcription | faster-whisper (base.en, CPU int8) |
| Summarisation | Ollama + Llama 3.2 3B |
| Backend API | FastAPI + Uvicorn |
| Database | SQLite |
| Workflow Automation | n8n (Self-hosted) |

## Live Application

You can view the deployed Streamlit frontend here: 
[Live NEC Meeting Summariser](https://nec-ai-meeting-summariser-ma5nfdgcf5bey7asreevd6.streamlit.app/)

(Note: The frontend requires the FastAPI backend to be running locally or via a Cloudflare tunnel to process new audio).

## Files

- app.py - Streamlit frontend interface
- api.py - FastAPI backend with /process, /meetings, /health endpoints
- pipeline.py - Core transcription, summarisation, and notification pipeline
- meetings.db - SQLite database of past meetings

## Setup (Local Development)

### Prerequisites

- Python 3.11+
- Ollama installed (ollama.com)
- At least 8 GB RAM

### Install Dependencies

pip install faster-whisper fastapi uvicorn python-multipart streamlit requests
pip install "av>=13.0.0,<14.0.0"
ollama pull llama3.2:3b

### Run the Backend (FastAPI)

uvicorn api:app --host 0.0.0.0 --port 8000

### Run the Frontend (Streamlit)

streamlit run app.py

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | / | Service info |
| GET | /health | Health check |
| POST | /process | Upload audio, get summary & Slack notification |
| GET | /meetings | Retrieve meeting history |

## Status

- Backend (FastAPI): Complete
- Streamlit UI: Complete (Deployed to Cloud)
- n8n + Slack Integration: Complete
- End-to-end pipeline: Verified

## Author

Thebe Ledwaba - EINTP4A Capstone Project, VUT 2026
Student Number: 219119007
