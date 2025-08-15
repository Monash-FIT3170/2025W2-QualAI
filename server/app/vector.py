import os
from functools import lru_cache
import subprocess
import sys

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
    If collection doesn't exist, create it and run ingestion script.
    """
    print("Initializing vector store...")
    client = get_qdrant_client()
    embeddings = get_embeddings_model()

    try:
        # Check if collection exists
        collections_list = client.get_collections().collections
        collection_names = [c.name for c in collections_list]

        if QDRANT_COLLECTION_NAME not in collection_names:
            print(f"Collection '{QDRANT_COLLECTION_NAME}' not found. Creating...")

            client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config={
                    "size": embeddings.client.get_sentence_embedding_dimension(),
                    "distance": "Cosine"
                }
            )
            print(f"Collection '{QDRANT_COLLECTION_NAME}' created.")

            # Run ingestion script automatically
            print("Running ingestion pipeline to populate collection...")
            result = subprocess.run(
                [sys.executable, "/app/server/scripts/ingest.py"],  # Adjust path if needed
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("Ingestion failed:")
                print(result.stderr)
            else:
                print("Ingestion completed successfully.")
                print(result.stdout)

        else:
            print(f"Collection '{QDRANT_COLLECTION_NAME}' already exists.")

    except Exception as e:
        print(f"Error checking/creating collection: {e}")
        raise

    return Qdrant(
        client=client,
        embeddings=embeddings,
        collection_name=QDRANT_COLLECTION_NAME,
    )