from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import uuid

app = FastAPI()

# Initialize Qdrant client (adjust if running remotely)
qdrant = QdrantClient("qdrant", port=6333)

# Collection name and vector model setup
COLLECTION_NAME = "transcripts"
MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_SIZE = 384

# Create the collection (if it doesn't exist)
qdrant.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
)

# Load model once
model = SentenceTransformer(MODEL_NAME)


@app.get("/")
async def root():
    sentences = [
        "Thsadfe weather is lovely tsadfasfdoday.",
        "Isadft's so sunny outsasdfsadfide!",
        "He droasdfve to the stasdfsadfadium.",
    ]

    # Encode the sentences
    embeddings = model.encode(sentences)
    similarities = model.similarity(embeddings, embeddings)

    # Create and upsert points
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embeddings[i],
            payload={"text": sentences[i]}
        )
        for i in range(len(sentences))
    ]

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

    return {
        "status": embeddings.tolist(),
        "stored": similarities.tolist()
    }
