#load pdf 
#split into chunks 
#create the embeddings 
#store into chroma 
from langchain_community.document_loaders import PyPDFLoader
import os 
from langchain_chroma import Chroma 
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "meeting_transcript"
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"

data = PyPDFLoader("document loaders/deeplearning.pdf")
docs = data.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200
)

chunks = splitter.split_documents(docs)

embedding_model = HuggingFaceEmbeddings(
        model_name = EMBEDDING_MODEL,
        model_kwargs = {"device" : 'cpu'}
    )

vectorstore = Chroma.from_documents(
    documents= chunks,
    embedding=embedding_model,
    persist_directory="chroma_db"
)