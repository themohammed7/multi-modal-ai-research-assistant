from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Form

import os

from backend.services.audio_service import process_audio
from backend.services.audio_service import audio_sessions

from backend.core.rag_engine import ask_question

router = APIRouter()

UPLOAD_DIR = "uploads/audio"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...)
):

    filepath = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(filepath, "wb") as buffer:
        buffer.write(
            await file.read()
        )

    result = process_audio(
        filepath
    )

    return result


@router.post("/youtube")
async def youtube_audio(
    url: str = Form(...)
):

    result = process_audio(url)

    return result


from backend.schemas import AudioQuestion

from backend.schemas import AudioQuestion

@router.post("/ask")
async def ask_audio_question(
    data: AudioQuestion
):

    session = audio_sessions.get(
        data.session_id
    )

    if session is None:

        return {
            "answer":
            "Audio session not found."
        }

    rag_chain = session[
        "rag_chain"
    ]

    history = session[
        "history"
    ]

    history_text = "\n".join(
        [
            f"{msg['role']}: {msg['content']}"
            for msg in history
        ]
    )

    enhanced_question = f"""
Conversation History:

{history_text}

Current Question:

{data.question}
"""

    answer = ask_question(
        rag_chain,
        enhanced_question
    )

    history.append(
        {
            "role": "user",
            "content": data.question
        }
    )

    history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    return {
        "answer": answer
    }