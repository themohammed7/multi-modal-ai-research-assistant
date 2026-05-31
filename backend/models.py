from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from backend.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        default="New Chat"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    chat_id = Column(
        Integer,
        ForeignKey("chat_sessions.id")
    )

    role = Column(String)

    content = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class PDFSession(Base):
    __tablename__ = "pdf_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    file_name = Column(String)

    file_path = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class MeetingSession(Base):
    __tablename__ = "meeting_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(String)

    transcript_path = Column(String)

    summary_path = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )