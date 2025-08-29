import os
from functools import lru_cache
import subprocess
import sys

from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant,
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.documents import Document



QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION_NAME = "research_papers_v1"
EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"


def setup_qdrant_collection():
    """Ensures the Qdrant collection exists with the correct configuration."""
    client = get_qdrant_client()
    try:
        collections_list = client.get_collections().collections
        collection_names = [c.name for c in collections_list]

        if QDRANT_COLLECTION_NAME not in collection_names:
            print(f"Collection '{QDRANT_COLLECTION_NAME}' not found. Creating...")
            client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE, # Use the defined constant
                    distance=models.Distance.COSINE
                )
            )
            print(f"Collection '{QDRANT_COLLECTION_NAME}' created.")
            return True
        else:
            print(f"Collection '{QDRANT_COLLECTION_NAME}' already exists.")
            return False

    except Exception as e:
        print(f"Error setting up Qdrant collection: {e}")
        raise

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
def get_db() -> Qdrant:
    """
    Initializes a LangChain Qdrant vector store object.
    If collection doesn't exist or is empty, create it and run ingestion script.
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

        # Check if collection has any points
        stats = client.count(QDRANT_COLLECTION_NAME)
        if stats.count == 0:
            print("Collection is empty. Running ingestion pipeline...")

            # Correct path to ingest.py relative to vector.py
            from pathlib import Path
            script_path = Path("/app/scripts/ingest.py")

            result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)

            if result.returncode != 0:
                print("Ingestion failed:")
                print(result.stderr)
            else:
                print("Ingestion completed successfully.")
                print(result.stdout)
        else:
            print(f"Collection '{QDRANT_COLLECTION_NAME}' already populated with {stats.count} points.")

    except Exception as e:
        print(f"Error checking/creating collection: {e}")
        raise

    return Qdrant(
        client=client,
        embeddings=embeddings,
        collection_name=QDRANT_COLLECTION_NAME,
    )

def augment_prompt(prompt: str, project: str=None, transcript: str=None):
    context = get_context(prompt, project=project, transcript=transcript)

    prompt_context= "\n".join(fragment.page_content for fragment in context)

    metaprompt = f"""
    You are an academic research analyst.
    Answer the following question using the provided context. 
    If you can't find the answer, do not pretend you know it, but answer "I don't know".

    Question: {prompt.strip()}

    Context: 
    {prompt_context.strip()}

    Answer:
    """
    
    return metaprompt

def get_context(prompt: str, project: str=None, transcript: str=None) -> list[Document]:
    qdrant = get_db()

    response = qdrant.similarity_search(query=prompt)

    return response

