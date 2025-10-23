from fastapi import APIRouter, HTTPException
from app.config import config
from app.database import Highlight

highlight_router = APIRouter(prefix="/highlights", tags=["Highlights"])

# same database path as the rest of the app
highlight_db = Highlight(config.DB_PATH)

@highlight_router.post("/")
def add_highlight(transcription_id: int, start: int, end: int, color: str, comment: str = "", highlighter_id: int | None = None):
    highlight_db.insert(
        transcription_id=transcription_id,
        start=start,
        end=end,
        color=color,
        comment=comment,
        highlighter_id=highlighter_id
        
    )
    return {"message": "Highlight added successfully"}

@highlight_router.get("/{transcription_id}")
def get_highlights(transcription_id: int):
    highlights = highlight_db.get_all_for_transcription(transcription_id)
    if not highlights:
        raise HTTPException(status_code=404, detail="No highlights found")
    return highlights

# delete highlight
@highlight_router.delete("/{highlight_id}")
def delete_highlight(highlight_id: int):
    success = highlight_db.delete(highlight_id)
    if not success:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return {"message": f"Highlight {highlight_id} deleted successfully"}