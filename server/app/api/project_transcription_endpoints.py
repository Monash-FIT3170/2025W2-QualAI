from fastapi import APIRouter, Request
from fastapi import HTTPException

import app.api.helpers.transcription_converters as trans_conv
from app.api.models import TranscriptionRequest

transcription_router = APIRouter()


@transcription_router.post("/projects/{project_id}/transcriptions")
def add_transcription(
    request: Request, project_id: int, payload: TranscriptionRequest
) -> dict:
    """
    Attach a transcription to a specific project.
    """
    # Ensure project exists first (will raise LookupError -> 404)
    try:
        request.app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    new_id = request.app.state.transcripts_store.insert(
        project_id, payload.name, payload.text
    )
    # Optionally return minimal info with id, or the full record:
    proj_id, name, text, processed_at = (
        request.app.state.transcripts_store.get_transcription_by_id(new_id)
    )
    return {
        "transcription_id": new_id,
        "project_id": proj_id,
        "name": name,
        "text": text,
        "processed_at": processed_at,
    }


@transcription_router.get("/projects/{project_id}/transcriptions")
def list_transcriptions(request: Request, project_id: int) -> list[dict]:
    """
    List transcription metadata for a project (no full text).
    """
    # Ensure project exists
    try:
        request.app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    rows = request.app.state.transcripts_store.get_all_project_transcriptions(
        project_id
    )
    return [trans_conv.transcription_meta_row_to_dict(r) for r in rows]


@transcription_router.get("/projects/{project_id}/transcriptions/{transcription_id}")
def get_transcription(request: Request, project_id: int, transcription_id: int) -> dict:
    """
    Get a specific transcription by project and transcription ID.
    """
    # Ensure project exists
    try:
        request.app.state.projects_store.get_project_by_id(project_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get the transcription
    try:
        proj_id, name, text, processed_at = (
            request.app.state.transcripts_store.get_transcription_by_id(
                transcription_id
            )
        )

        # Verify the transcription belongs to the specified project
        if proj_id != project_id:
            raise HTTPException(
                status_code=404, detail="Transcription not found in this project"
            )

        return {
            "transcription_id": transcription_id,
            "project_id": proj_id,
            "name": name,
            "text": text,
            "processed_at": processed_at,
        }
    except LookupError:
        raise HTTPException(status_code=404, detail="Transcription not found")


@transcription_router.put("/projects/{project_id}/transcriptions/{transcription_id}")
def update_transcription(
    request: Request,
    project_id: int,
    transcription_id: int,
    payload: TranscriptionRequest,
):
    """
    Update a specific transcription by project and transcription ID.
    """
    # Ensure project exists
    try:
        project_name, _, _ = request.app.state.projects_store.get_project_by_id(
            project_id
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get the transcription first to verify it exists and belongs to the project
    try:
        proj_id, name, text, processed_at = (
            request.app.state.transcripts_store.get_transcription_by_id(
                transcription_id
            )
        )

        # Verify the transcription belongs to the spescified project
        if proj_id != project_id:
            raise HTTPException(
                status_code=404, detail="Transcription not found in this project"
            )
    except LookupError:
        raise HTTPException(status_code=404, detail="Transcription not found")

    # Update the transcription in the database
    try:
        request.app.state.transcripts_store.update(transcription_id, payload.text)
        print(f"Updated transcription {transcription_id} in project {project_id}")

        # Update the vector database with the new content
        try:
            request.app.state.qdrant_manager.clear_collection(proj_id)
            request.app.state.qdrant_manager.ingest_from_text(proj_id, payload.text)
            print(f"Updated vector database for project: {project_name}")
        except Exception as vector_error:
            print(
                f"Warning: Failed to update vector database for project '{project_name}': {vector_error}"
            )
            # Don't fail the entire operation if vector update fails

        # Return the updated transcription
        proj_id, name, text, processed_at = (
            request.app.state.transcripts_store.get_transcription_by_id(
                transcription_id
            )
        )
        return {
            "transcription_id": transcription_id,
            "project_id": proj_id,
            "name": name,
            "text": text,
            "processed_at": processed_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update transcription: {e}"
        )


@transcription_router.delete("/projects/{project_id}/transcriptions/{transcription_id}")
def delete_transcription(request: Request, project_id: int, transcription_id: int):
    """
    Delete a specific transcription by project and transcription ID.
    """
    # Ensure project exists
    try:
        project_name, _, _ = request.app.state.projects_store.get_project_by_id(
            project_id
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get the transcription first to verify it exists and belongs to the project
    try:
        proj_id, name, text, processed_at = (
            request.app.state.transcripts_store.get_transcription_by_id(
                transcription_id
            )
        )

        # Verify the transcription belongs to the specified project
        if proj_id != project_id:
            raise HTTPException(
                status_code=404, detail="Transcription not found in this project"
            )
    except LookupError:
        raise HTTPException(status_code=404, detail="Transcription not found")

    # Delete the transcription from the database
    try:
        request.app.state.transcripts_store.delete(transcription_id)
        print(f"Deleted transcription {transcription_id} from project {project_id}")

        try:
            ### TODO
            ### IMPORTANT - Transcript should be removed from project
            pass

        except Exception as vector_error:
            print(
                f"Warning: Failed to update vector database for project '{project_name}': {vector_error}"
            )
            # Don't fail the entire operation if vector update fails

        return {"ok": True, "message": "Transcription deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete transcription: {e}"
        )
