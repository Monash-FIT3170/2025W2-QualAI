from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from .vector import get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Loading models and connecting to DB...")
    get_db()
    print("Application startup complete.")
    yield
    print("Application shutdown: Cleaning up resources...")


app = FastAPI(title="Vector-Search API", lifespan=lifespan)


class SearchResponse(BaseModel):
    result: list[dict]

@app.get("/")
def read_root():
    return {"message": "API is running. Use the /search endpoint to query."}


@app.get("/search", response_model=SearchResponse)
async def search(q: str = Query(..., min_length=2), k: int = 5):
    """
    Performs a similarity search in the Qdrant vector database.
    """

    db = get_db()
    try:
        # Use similarity_search_with_score to get both the document and the score
        docs_with_scores = db.similarity_search_with_score(query=q, k=k)
    except Exception as e:
        # If there's an error during the search, return a 500 internal server error
        raise HTTPException(status_code=500, detail=str(e))

    # Format the results into the desired JSON structure
    return {
        "result": [
            {
                # "score": score,  I comented this out as it is basically meta data
                "content": doc.page_content.replace('\n', ' ').strip(),
                # "metadata": doc.metadata
            }
            for doc, score in docs_with_scores
        ]
    }