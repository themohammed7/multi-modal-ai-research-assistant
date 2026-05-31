import os

from backend.database import SessionLocal
from backend.models import MeetingSession

from backend.core.audio_processor import process_input
from backend.core.transciber import transcribe_all
from backend.core.summarizer import (
    summarize,
    generate_title
)
from backend.core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions
)
from backend.core.rag_engine import build_rag_chain

# In-memory RAG chains
# (Later we can load dynamically)
audio_sessions = {}

TRANSCRIPT_DIR = "uploads/transcript"
SUMMARY_DIR = "uploads/summary"

os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)


def process_audio(
    source: str,
    language: str = "english"
):

    print("Starting audio processing...")

    # =====================================
    # AUDIO -> CHUNKS
    # =====================================

    chunks = process_input(source)
    print(f"Total chunks created: {len(chunks)}")

    # =====================================
    # TRANSCRIPTION
    # =====================================

    transcript = transcribe_all(
        chunks,
        language
    )

    # =====================================
    # SUMMARY + TITLE
    # =====================================

    title = generate_title(transcript)

    summary = summarize(transcript)

    # =====================================
    # EXTRACTIONS
    # =====================================

    actions = extract_action_items(
        transcript
    )

    decisions = extract_key_decisions(
        transcript
    )

    questions = extract_questions(
        transcript
    )

    # =====================================
    # DATABASE ENTRY
    # =====================================

    db = SessionLocal()

    meeting = MeetingSession(
        title=title,
        transcript_path="",
        summary_path=""
    )

    db.add(meeting)

    db.commit()

    db.refresh(meeting)

    session_id = meeting.id

    # =====================================
    # SAVE TRANSCRIPT
    # =====================================

    transcript_file = os.path.join(
        TRANSCRIPT_DIR,
        f"meeting_{session_id}.txt"
    )

    with open(
        transcript_file,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(transcript)

    # =====================================
    # SAVE SUMMARY
    # =====================================

    summary_file = os.path.join(
        SUMMARY_DIR,
        f"meeting_{session_id}.txt"
    )

    with open(
        summary_file,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(summary)

    # =====================================
    # UPDATE DATABASE PATHS
    # =====================================

    meeting.transcript_path = transcript_file
    meeting.summary_path = summary_file

    db.commit()

    db.close()

    # =====================================
    # BUILD RAG CHAIN
    # =====================================

    rag_chain = build_rag_chain(
        transcript
    )

    audio_sessions[
    session_id
] = {
    "rag_chain": rag_chain,
    "history": [],
    "summary": summary,
    "actions": actions,
    "decisions": decisions,
    "questions": questions
}

    # =====================================
    # RESPONSE
    # =====================================

    return {
        "session_id": session_id,
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "actions": actions,
        "decisions": decisions,
        "questions": questions
    }
    
