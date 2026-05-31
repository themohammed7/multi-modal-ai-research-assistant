from pydantic import BaseModel


class ChatCreate(BaseModel):
    pass


class ChatMessage(BaseModel):
    chat_id: int
    message: str


class DeleteChat(BaseModel):
    chat_id: int


class AudioQuestion(BaseModel):
    session_id: int
    question: str


class PDFQuestion(BaseModel):
    session_id: int
    question: str