from functools import lru_cache
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from qdrant_client import QdrantClient
import os

COLLECTION = "test_db"
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")   # docker-compose service name

@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": False},
    )

@lru_cache(maxsize=1)
def get_db():
    client = QdrantClient(url=QDRANT_URL, prefer_grpc=False)
    return Qdrant(
        client=client,
        embeddings=get_embeddings(),
        collection_name=COLLECTION,
    )

