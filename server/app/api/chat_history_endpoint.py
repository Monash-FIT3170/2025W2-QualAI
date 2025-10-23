from fastapi import APIRouter, Request, HTTPException

from app.api.models import ChatMessageRequest

chat_history_router = APIRouter()


@chat_history_router.post("/projects/{project_id}/chat")
def add_chat_message(request: Request, project_id: int, payload: ChatMessageRequest):
    """
    Add a chat message to the project's chat history.
    """
    # Ensure project exists
    try:
        request.app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    # Basic validation of sender
    sender = (payload.sender or "").strip().lower()
    if sender not in ("user", "ai"):
        raise HTTPException(
            status_code=400, detail="sender must be 'user' or 'ai'"
        )

    # Insert chat message using chat_history_store
    message_id = request.app.state.chat_history_store.insert(
        project_id=project_id, sender=sender, message=payload.message
    )

    return {
        "ok": True,
        "message": "Chat message added successfully",
        "message_id": message_id
    }


@chat_history_router.get("/projects/{project_id}/chat")
def list_chat_messages(request: Request, project_id: int) -> list[dict]:
    """
    List chat messages for a project ordered by time.
    """
    # Ensure project exists
    try:
        request.app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get chat messages from chat_history_store
    rows = request.app.state.chat_history_store.get_all_project_chat_messages(
        project_id
    )

    return [
        {
            "message_id": message_id,
            "sender": sender,
            "text": text,
            "created_at": created_at
        }
        for (message_id, sender, text, created_at) in rows
    ]


@chat_history_router.delete("/projects/{project_id}/chat/{message_id}")
def delete_chat_message(request: Request, project_id: int, message_id: int):
    """
    Delete a specific chat message.
    """
    # Ensure project exists
    try:
        request.app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Verify message belongs to project and delete it
        request.app.state.chat_history_store.delete(message_id, project_id)
        return {"ok": True, "message": "Chat message deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete chat message: {e}"
        )
