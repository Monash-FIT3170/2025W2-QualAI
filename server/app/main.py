from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from .vector import get_db
from .routes import hello

# Initialize the FastAPI application with a title
app = FastAPI(title="Vector-Search API")


app.include_router(hello.router)   # ← mount its routes


class SearchResponse(BaseModel):
    result: list[dict]


# Define a GET endpoint `/search` with a response model and query parameters
@app.get("/search", response_model=SearchResponse)
async def search(q: str = Query(..., min_length=2), k: int = 5):
    db = get_db()
    try:
        # Perform a similarity search in the vector DB using the query string `q` and return top `k` results
        docs = db.similarity_search_with_score(query=q, k=k)
    except Exception as e:
        raise HTTPException(500, str(e))

    return {
        "result": [
            # Format and return the search results: score, document content, and metadata
            {"score": score, "content": doc.page_content, "metadata": doc.metadata}
            for doc, score in docs
        ]
    }