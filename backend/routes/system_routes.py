from fastapi import APIRouter
from sqlalchemy import text
import os
import shutil

from backend.database import SessionLocal
from backend.models import (
    Message,
    ChatSession,
    PDFSession,
    MeetingSession
)

router = APIRouter()


@router.delete("/wipe-all")
def wipe_all():

    db = SessionLocal()

    # =====================
    # Clear database tables
    # =====================

    db.query(Message).delete()
    db.query(ChatSession).delete()
    db.query(PDFSession).delete()
    db.query(MeetingSession).delete()

    db.commit()

    # Reset SQLite IDs

    try:
        db.execute(
            text("DELETE FROM sqlite_sequence")
        )
        db.commit()
    except Exception:
        pass

    db.close()

    # =====================
    # Delete files only
    # =====================

    folders = [
        "uploads/audio",
        "uploads/pdf",
        "uploads/transcript",
        "uploads/summary",
        "vector_db",
        "downloades"
    ]

    for folder in folders:

        if not os.path.exists(folder):
            continue

        for item in os.listdir(folder):

            item_path = os.path.join(
                folder,
                item
            )

            try:

                if os.path.isfile(item_path):

                    os.remove(item_path)

                elif os.path.isdir(item_path):

                    shutil.rmtree(
                        item_path,
                        ignore_errors=True
                    )

            except Exception as e:

                print(
                    f"Failed deleting {item_path}: {e}"
                )

    return {
        "message":
        "Everything erased successfully"
    }