# query.py

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from .vector import get_db  # Assuming vector.py (or vector folder) is in the same directory

# Initialize an APIRouter
router = APIRouter()

class SearchResponse(BaseModel):
    result: list[dict]

# Define a GET endpoint `/search` with a response model and query parameters
@router.get("/search", response_model=SearchResponse, tags=["Search"]) # Added a tag for better docs
async def search_query(q: str = Query(..., min_length=2), k: int = 5): # Renamed function to avoid conflict if imported directly
    db = get_db()
    try:
        # Perform a similarity search in the vector DB using the query string `q` and return top `k` results
        docs = db.similarity_search_with_score(query=q, k=k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "result": [
            # Format and return the search results: score, document content, and metadata
            {"score": score, "content": doc.page_content, "metadata": doc.metadata}
            for doc, score in docs
        ]
    }