from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from .vector import get_db
from .routes import hello


app = FastAPI(title="Vector-Search API")


app.include_router(hello.router)   # ← mount its routes


class SearchResponse(BaseModel):
    result: list[dict]

@app.get("/search", response_model=SearchResponse)
async def search(q: str = Query(..., min_length=2), k: int = 5):
    db = get_db()
    try:
        docs = db.similarity_search_with_score(query=q, k=k)
    except Exception as e:
        raise HTTPException(500, str(e))

    return {
        "result": [
            {"score": score, "content": doc.page_content, "metadata": doc.metadata}
            for doc, score in docs
        ]
