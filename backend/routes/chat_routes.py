from fastapi import APIRouter
from sqlalchemy.orm import Session

from backend.database import SessionLocal

from backend.models import (
    ChatSession,
    Message
)

from backend.schemas import (
    ChatMessage
)

from backend.services.chatbot_service import (
    get_ai_response
)

router = APIRouter()


# ==========================
# CREATE NEW CHAT
# ==========================

@router.post("/new-chat")
def create_chat():

    db: Session = SessionLocal()

    chat = ChatSession(
        title="New Chat"
    )

    db.add(chat)

    db.commit()

    db.refresh(chat)

    chat_id = chat.id

    db.close()

    return {
        "chat_id": chat_id
    }


# ==========================
# GET ALL CHATS
# ==========================

@router.get("/history")
def get_history():

    db: Session = SessionLocal()

    chats = db.query(
        ChatSession
    ).order_by(
        ChatSession.id.desc()
    ).all()

    result = []

    for chat in chats:

        result.append(
            {
                "id": chat.id,
                "title": chat.title
            }
        )

    db.close()

    return result


# ==========================
# GET CHAT MESSAGES
# ==========================

@router.get("/messages/{chat_id}")
def get_messages(chat_id: int):

    db: Session = SessionLocal()

    msgs = db.query(
        Message
    ).filter(
        Message.chat_id == chat_id
    ).order_by(
        Message.id.asc()
    ).all()

    result = []

    for msg in msgs:

        result.append(
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content
            }
        )

    db.close()

    return result


# ==========================
# SEND MESSAGE
# ==========================

@router.post("/send")
def send_message(
    data: ChatMessage
):

    db: Session = SessionLocal()

    # Save User Message

    user_msg = Message(
        chat_id=data.chat_id,
        role="user",
        content=data.message
    )

    db.add(user_msg)

    db.commit()

    db.refresh(user_msg)

    # Load Full Conversation History

    history = db.query(
        Message
    ).filter(
        Message.chat_id == data.chat_id
    ).order_by(
        Message.id.asc()
    ).all()

    # Generate AI Response

    ai_response = get_ai_response(
        history
    )

    # Save Assistant Message

    bot_msg = Message(
        chat_id=data.chat_id,
        role="assistant",
        content=ai_response
    )

    db.add(bot_msg)

    db.commit()

    db.refresh(bot_msg)

    user_message_id = user_msg.id
    assistant_message_id = bot_msg.id

    # Update Chat Title

    chat = db.query(
        ChatSession
    ).filter(
        ChatSession.id == data.chat_id
    ).first()

    if (
        chat
        and
        chat.title == "New Chat"
    ):

        chat.title = data.message[:40]

        db.commit()

    db.close()

    return {
        "response": ai_response,
        "user_message_id": user_message_id,
        "assistant_message_id": assistant_message_id
    }


# ==========================
# DELETE ONE MESSAGE
# ==========================

@router.delete("/message/{message_id}")
def delete_message(
    message_id: int
):

    db: Session = SessionLocal()

    msg = db.query(
        Message
    ).filter(
        Message.id == message_id
    ).first()

    if msg:

        db.delete(msg)

        db.commit()

    db.close()

    return {
        "message": "Message deleted"
    }


# ==========================
# DELETE CHAT
# ==========================

@router.delete("/history/{chat_id}")
def delete_chat_history(
    chat_id: int
):

    db: Session = SessionLocal()

    db.query(
        Message
    ).filter(
        Message.chat_id == chat_id
    ).delete()

    db.query(
        ChatSession
    ).filter(
        ChatSession.id == chat_id
    ).delete()

    db.commit()

    db.close()

    return {
        "message": "Chat deleted"
    }


# ==========================
# RENAME CHAT
# ==========================

@router.put("/rename/{chat_id}")
def rename_chat(
    chat_id: int,
    title: str
):

    db: Session = SessionLocal()

    chat = db.query(
        ChatSession
    ).filter(
        ChatSession.id == chat_id
    ).first()

    if chat:

        chat.title = title

        db.commit()

    db.close()

    return {
        "message": "Chat renamed"
    }