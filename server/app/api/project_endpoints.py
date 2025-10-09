from fastapi import APIRouter, Request
from fastapi import HTTPException
import sqlite3

from app.api.helpers.project_converters import (
    project_row_to_dict,
    project_full_row_to_dict,
)
from app.api.models import ProjectRequest, ChatMessageRequest
from app.config import config

project_router = APIRouter()


@project_router.post("/projects")
def create_project(request: Request, payload: ProjectRequest):
    """
    Create a new project. Name must be unique (sqlite UNIQUE constraint).
    """
    try:
        new_id = request.app.state.projects_store.insert(
            payload.name, payload.description or ""
        )
    except sqlite3.IntegrityError:
        # UNIQUE(name) violated
        raise HTTPException(
            status_code=400, detail="Project name already exists.")

    # fetch and return canonical row
    name, desc, created_at = request.app.state.projects_store.get_project_by_id(
        new_id)
    return project_row_to_dict(new_id, (name, desc, created_at))


@project_router.get("/projects")
def list_projects(request: Request) -> list[dict]:
    """
    List all projects. If DB is empty, create a default 'Project 1' and return it.
    """
    rows = request.app.state.projects_store.get_all_projects()
    if not rows:
        # auto-create default to keep UX consistent with your current app
        try:
            default_id = request.app.state.projects_store.insert(
                config.DEFAULT_PROJECT)
            name, desc, created_at = request.app.state.projects_store.get_project_by_id(
                default_id
            )
            return project_row_to_dict(default_id, (name, desc, created_at))
        except sqlite3.IntegrityError:
            # extremely unlikely race; just refetch all
            rows = request.app.state.projects_store.get_all_projects()

    return [project_full_row_to_dict(r) for r in rows]


@project_router.get("/projects/{project_id}")
def get_project(request: Request, project_id: int) -> dict:
    """
    Get a single project by id.
    """
    try:
        name, desc, created_at = request.app.state.projects_store.get_project_by_id(
            project_id
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    return project_row_to_dict(project_id, (name, desc, created_at))


@project_router.delete("/projects/{project_id}")
def delete_project(request: Request, project_id: int):
    """
    Delete a project by id.
    Also deletes the corresponding Qdrant collection.
    """
    try:
        # Delete the project from the database (this will also delete associated transcriptions due to foreign key cascade)
        request.app.state.projects_store.delete(project_id)

        # Delete the corresponding Qdrant collection
        try:
            request.app.state.qdrant_manager.clear_collection(project_id)
            print(f"Deleted Qdrant collection for project: {project_id}")
        except Exception as qdrant_error:
            print(
                f"Warning: Failed to delete Qdrant collection for project '{project_id}': {qdrant_error}"
            )
            # Don't fail the entire operation if Qdrant deletion fails

        return {"ok": True, "message": "Project deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete project: {e}")


@project_router.post("/projects/{project_id}/chat")
def add_chat_message(request: Request, project_id: int, payload: ChatMessageRequest):
    """
    Add a chat message to the project's chat history (normalized table).
    """
    # Basic validation of sender
    sender = (payload.sender or "").strip().lower()
    if sender not in ("user", "ai"):
        raise HTTPException(
            status_code=400, detail="sender must be 'user' or 'ai'")

    request.app.state.projects_store.add_chat_message(
        project_id, sender, payload.message)
    return {"ok": True, "message": "Chat message added successfully"}


@project_router.get("/projects/{project_id}/chat")
def list_chat_messages(request: Request, project_id: int) -> list[dict]:
    """
    List chat messages for a project ordered by time.
    """
    rows = request.app.state.projects_store.get_chat_messages(project_id)
    return [
        {"sender": sender, "text": text, "created_at": created_at}
        for (sender, text, created_at) in rows
    ]
