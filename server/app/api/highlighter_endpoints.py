from fastapi import APIRouter, HTTPException, Request
from app.api.models import HighlighterRequest
import sqlite3
from app.config import config

highlighter_router = APIRouter(prefix="/projects/{project_id}/highlighters")


@highlighter_router.post("/")
def create_highlighter(request: Request, data: HighlighterRequest, project_id: int):
    """
    Create a new highlighter for a given project.
    """
    try:
        request.app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        highlighter_id = request.app.state.highlighter_store.insert(
            project_id,
            data.label,
            data.colour,
            str(data.weight),  # stored as text
        )

        return {
            "highlighter_id": highlighter_id,
            "message": "Highlighter created successfully.",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create highlighter: {e}")


@highlighter_router.get("/")
def get_highlighters_by_project(request: Request, project_id: int):
    """
    Get all highlighters for a specific project.
    """
    try:
        request.app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        rows = request.app.state.highlighter_store.get_highlighters_by_project(project_id)
        return [
            {
                "highlighter_id": r[0],
                "label": r[1],
                "colour": r[2],
                "weight": r[3],
                "created_at": r[4],
                "updated_at": r[5],
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch highlighters: {e}")


@highlighter_router.put("/{highlighter_id}")
def update_highlighter(
    request: Request, data: HighlighterRequest, project_id: int, highlighter_id: int
):
    """
    Update an existing highlighter.
    """
    try:
        request.app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        request.app.state.highlighter_store.update(
            highlighter_id,
            label=data.label,
            colour=data.colour,
            weight=str(data.weight),
        )

        with sqlite3.connect(config.DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                UPDATE {config.DB_HIGHLIGHT_TABLE_NAME}
                SET color = ?
                WHERE highlighter_id = ?
                """,
                (data.colour, highlighter_id),
            )
            conn.commit()
        
        return {"message": "Highlighter updated successfully."}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update highlighter: {e}")


@highlighter_router.delete("/{highlighter_id}")
def delete_highlighter(request: Request, project_id: int, highlighter_id: int):
    """
    Delete an existing highlighter.
    """
    try:
        request.app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        request.app.state.highlighter_store.delete(highlighter_id)
        return {"message": "Highlighter deleted successfully."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete highlighter: {e}")
