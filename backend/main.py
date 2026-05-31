from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base
from backend.database import engine

from backend.routes.chat_routes import router as chat_router
from backend.routes.audio_routes import router as audio_router
from backend.routes.pdf_routes import router as pdf_router
from backend.routes.system_routes import router as system_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Assistant API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Chatbot
app.include_router(
    chat_router,
    prefix="/chat",
    tags=["Chat"]
)

# Audio Assistant
app.include_router(
    audio_router,
    prefix="/audio",
    tags=["Audio"]
)

# PDF Assistant
app.include_router(
    pdf_router,
    prefix="/pdf",
    tags=["PDF"]
)

app.include_router(
    system_router,
    prefix="/system",
    tags=["System"]
)

@app.get("/")
def root():
    return {
        "message": "AI Assistant Running"
    }