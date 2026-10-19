
"""
NEC AI Meeting Summariser - Streamlit Frontend
Uploads audio, runs the pipeline, and displays results.
"""

import streamlit as st
import requests
import tempfile
import os
import json

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="NEC AI Meeting Summariser",
    page_icon="🎙️",
    layout="wide"
)

# ---------- Header ----------
st.title("NEC AI Meeting Summariser")
st.markdown(
    "Upload a short meeting recording and get a **summary** plus "
    "**action items** — entirely offline, using local AI models."
)

st.divider()

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Settings")
    st.markdown("**Model configuration**")
    st.markdown("- Transcription: faster-whisper base.en")
    st.markdown("- Summarisation: Llama 3.2 3B")
    st.markdown("- Storage: SQLite (local)")
    st.divider()
    st.markdown("**About**")
    st.markdown(
        "This tool runs entirely offline. No audio or transcript "
        "leaves your machine."
    )

# ---------- Tabs ----------
tab1, tab2 = st.tabs(["Process Meeting", "Meeting History"])

# ============ TAB 1: PROCESS ============
with tab1:
    st.header("Upload a meeting recording")

    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=["mp3", "wav", "m4a", "ogg", "flac", "webm"]
    )

    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/mpeg")

        if st.button("Process meeting", type="primary"):
            with st.spinner("Running pipeline — this may take 30–90 seconds..."):
                try:
                    # Save uploaded file to temp
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=os.path.splitext(uploaded_file.name)[1]
                    ) as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name

                    # Send to FastAPI
                    with open(tmp_path, "rb") as f:
                        files = {
                            "audio": (
                                uploaded_file.name,
                                f,
                                uploaded_file.type or "audio/mpeg"
                            )
                        }
                        response = requests.post(
                            f"{API_URL}/process",
                            files=files,
                            timeout=600
                        )

                    os.remove(tmp_path)

                    if response.status_code == 200:
                        result = response.json()

                        st.success("Meeting processed successfully")

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Duration", f"{result['duration_seconds']:.1f}s")
                        with col2:
                            st.metric("Audio file", result["audio_filename"])

                        st.subheader("Transcript")
                        st.text_area(
                            "Full transcription",
                            result["transcript"],
                            height=150,
                            label_visibility="collapsed"
                        )

                        st.subheader("Summary and Action Items")
                        st.markdown(result["summary"])

                    else:
                        st.error(
                            f"API error {response.status_code}: {response.text}"
                        )

                except requests.exceptions.Timeout:
                    st.error("The pipeline timed out. Try a shorter recording.")
                except Exception as e:
                    st.error(f"Pipeline failed: {e}")

# ============ TAB 2: HISTORY ============
with tab2:
    st.header("Past meetings")

    if st.button("Refresh", type="secondary"):
        st.rerun()

    try:
        response = requests.get(f"{API_URL}/meetings?limit=20", timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.caption(f"{data['count']} meetings in database")

            for m in data["meetings"]:
                with st.expander(
                    f"Meeting #{m['id']} — {m['audio_filename']} "
                    f"({m['duration_seconds']:.1f}s)"
                ):
                    st.caption(f"Recorded: {m['timestamp']}")
                    st.markdown(m["summary"])
        else:
            st.error(f"Failed to load meetings: {response.status_code}")
    except Exception as e:
        st.error(f"Could not connect to API: {e}")

    st.divider()
    st.caption(
        "Every processed meeting is logged locally. "
        "No data is sent to external servers."
    )
