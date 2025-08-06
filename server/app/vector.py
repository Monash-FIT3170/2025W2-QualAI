import os
from functools import lru_cache

from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceBgeEmbeddings


QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION_NAME = "research_papers_v1"
EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"


@lru_cache(maxsize=1)
def get_embeddings_model():
    """
    Loads the BGE embedding model from Hugging Face.
    The model is cached for performance.
    """
    print("Loading embedding model...")
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    return HuggingFaceBgeEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )

@lru_cache(maxsize=1)
def get_qdrant_client():
    """
    Initializes and returns a Qdrant client instance.
    The client is cached for performance.
    """
    print("Connecting to Qdrant...")
    return QdrantClient(url=QDRANT_URL, prefer_grpc=False)

@lru_cache(maxsize=1)
def get_db():
    """
    Initializes a LangChain Qdrant vector store object.
    This is the main function to be imported by the API.
    """
    print("Initializing vector store...")
    client = get_qdrant_client()
    embeddings = get_embeddings_model()
    return Qdrant(
        client=client,
        embeddings=embeddings,
        collection_name=QDRANT_COLLECTION_NAME,
    )