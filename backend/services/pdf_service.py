import os

from backend.database import SessionLocal
from backend.models import PDFSession

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from backend.core.summarizer import summarize

PDF_DB = "vector_db/pdf"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

pdf_sessions = {}

os.makedirs(PDF_DB, exist_ok=True)


def create_pdf_rag(pdf_path):

    # ==========================
    # SAVE PDF SESSION TO DB
    # ==========================

    db = SessionLocal()

    pdf_record = PDFSession(
        file_name=os.path.basename(pdf_path),
        file_path=pdf_path
    )

    db.add(pdf_record)

    db.commit()

    db.refresh(pdf_record)

    session_id = pdf_record.id

    db.close()

    # ==========================
    # LOAD PDF
    # ==========================

    loader = PyPDFLoader(pdf_path)

    docs = loader.load()
    pdf_text = "\n".join(
    [
        doc.page_content
        for doc in docs
    ]
)

    summary = summarize(pdf_text)

    # ==========================
    # SPLIT
    # ==========================

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(
        docs
    )

    # ==========================
    # EMBEDDINGS
    # ==========================

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu"
        }
    )

    # ==========================
    # VECTOR STORE
    # ==========================

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PDF_DB
    )

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 4,
            "fetch_k": 10,
            "lambda_mult": 0.5
        }
    )

    # ==========================
    # LLM
    # ==========================

    llm = ChatMistralAI(
        model="mistral-small-latest"
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are an intelligent PDF Research Assistant.

Your primary task is to analyze the provided PDF context thoroughly and answer questions using the PDF content as accurately as possible.

Guidelines:

1. Carefully analyze the entire PDF context, including small details, tables, numbers, definitions, examples, and explanations.

2. Use conversation history when answering follow-up questions such as:

   . summarize above
   . explain more
   . what does this mean
   . give key points
   . simplify this
   . compare with previous answer

3. If the answer exists in the PDF, answer using the PDF information.

4. If the user asks a general question that is not related to the PDF, answer normally using your own knowledge and clearly indicate that the answer is outside the PDF context.

5. If the user asks for:

   . summary
   . key points
   . explanation
   . examples
   . simplification
   . action items
     then generate them from the PDF content and conversation history.

6. Never invent information and never claim something exists in the PDF if it does not.

7. If the answer cannot be found in the PDF and is not a general knowledge question, respond:

"I could not find the answer in the PDF."

8. Maintain a helpful, conversational, and intelligent assistant behavior while staying grounded in the PDF whenever relevant.

9. For factual PDF questions, prioritize PDF content over your general knowledge.

10. Provide complete and detailed answers whenever sufficient information is available in the PDF context.

"""
        ),
        (
            "human",
            """
Context:
{context}

Question:
{question}
"""
        )
    ])

    # ==========================
    # SAVE SESSION
    # ==========================

    pdf_sessions[session_id] = {
    "retriever": retriever,
    "llm": llm,
    "prompt": prompt,
    "history": [],
    "summary": summary
}

    return {
    "session_id": session_id,
    "summary": summary
}


def ask_pdf_question(
    session_id,
    question
):

    session = pdf_sessions.get(
        session_id
    )

    if not session:

        return (
            "PDF session not found. "
            "Please upload PDF again."
        )

    docs = session[
        "retriever"
    ].invoke(question)

    context = "\n\n".join(
        [
            doc.page_content
            for doc in docs
        ]
    )

    history_text = "\n".join(
        [
            f"{msg['role']}: {msg['content']}"
            for msg in session["history"]
        ]
    )

    final_prompt = session[
        "prompt"
    ].invoke(
        {
            "context":
            f"""
Conversation History:
{history_text}

PDF Context:
{context}
""",
            "question": question
        }
    )

    response = session[
        "llm"
    ].invoke(final_prompt)

    answer = response.content

    session["history"].append(
        {
            "role": "user",
            "content": question
        }
    )

    session["history"].append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    return answer
