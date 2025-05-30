from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent   # /app or server
TXT_PATH = BASE_DIR / "data" / "data.txt"           # /app/data/data.txt

loader = TextLoader(str(TXT_PATH), encoding='utf-8')

documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

texts = text_splitter.split_documents(documents)

# Load the embedding model
model_name = "BAAI/bge-base-en-v1.5"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}

embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

print("Embedding Model Loaded .......")

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
collection_name = "test_db"

qdrant = Qdrant.from_documents(
    texts,
    embeddings,
    url=QDRANT_URL,
    prefer_grpc=False,
    collection_name=collection_name
)

print("Qdrant Vector Database Created.........")
