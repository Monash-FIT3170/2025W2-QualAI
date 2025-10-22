# app/api/endpoints/pdf_ingest_endpoints.py
import os
from pathlib import Path
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from app.config import config

pdf_router = APIRouter(prefix="/ingest", tags=["PDF Ingestion"])

@pdf_router.post("/pdf")
async def ingest_pdf(
    request: Request,
    file: UploadFile = File(..., description="Upload a PDF for vector ingestion."),
    project_id: int = Form(...),
):
    """
    Extract text per-page from the uploaded PDF, split into semantic chunks,
    and upsert into Qdrant for RAG retrieval.
    """
    upload_dir = config.BASE_PATH / "PDF_Uploads"
    upload_dir.mkdir(exist_ok=True)
    pdf_path = upload_dir / (file.filename or "uploaded.pdf")

    try:
        with open(pdf_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    try:
        qdrant_mgr = request.app.state.qdrant_manager
        qdrant_mgr.ingest_pdf(project_id, str(pdf_path))

        # Optionally remove file after ingestion
        os.remove(pdf_path)
        return {"ok": True, "message": f"PDF '{file.filename}' ingested successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF ingestion failed: {e}")
# app/api/endpoints/pdf_ingest_endpoints.py
import os
from pathlib import Path
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from app.config import config

pdf_router = APIRouter(prefix="/ingest", tags=["PDF Ingestion"])

@pdf_router.post("/pdf")
async def ingest_pdf(
    request: Request,
    file: UploadFile = File(..., description="Upload a PDF for vector ingestion."),
    project_id: int = Form(...),
):
    """
    Extract text per-page from the uploaded PDF, split into semantic chunks,
    and upsert into Qdrant for RAG retrieval.
    """
    upload_dir = config.BASE_PATH / "PDF_Uploads"
    upload_dir.mkdir(exist_ok=True)
    pdf_path = upload_dir / (file.filename or "uploaded.pdf")

    try:
        with open(pdf_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    try:
        qdrant_mgr = request.app.state.qdrant_manager
        qdrant_mgr.ingest_pdf(project_id, str(pdf_path))

        # Optionally remove file after ingestion
        os.remove(pdf_path)
        return {"ok": True, "message": f"PDF '{file.filename}' ingested successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF ingestion failed: {e}")
