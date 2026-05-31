from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Form

import os

from backend.services.pdf_service import (
    create_pdf_rag,
    ask_pdf_question
)

router = APIRouter()

PDF_UPLOAD_DIR = "uploads/pdf"

os.makedirs(
    PDF_UPLOAD_DIR,
    exist_ok=True
)

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    filepath = os.path.join(
        PDF_UPLOAD_DIR,
        file.filename
    )

    with open(filepath, "wb") as buffer:
        buffer.write(
            await file.read()
        )

    result = create_pdf_rag(
        filepath
)

    return {
    "session_id": result["session_id"],
    "summary": result["summary"],
    "message": "PDF processed successfully"
}


from backend.schemas import PDFQuestion

@router.post("/ask")
async def ask_pdf(
    data: PDFQuestion
):

    answer = ask_pdf_question(
        data.session_id,
        data.question
    )

    return {
        "answer": answer
    }