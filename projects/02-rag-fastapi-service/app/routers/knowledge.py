from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas import ApiResponse
from app.services.document_loader import read_document_bytes, validate_extension
from app.services.rag_service import rag_service


router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


@router.post("/documents/upload", response_model=ApiResponse)
async def upload_document(file: UploadFile = File(...)) -> ApiResponse:
    try:
        validate_extension(file.filename or "")
        content = await file.read()
        text = read_document_bytes(file.filename or "document.txt", content)
        document = rag_service.add_text(file.filename or "document.txt", text, file.content_type or "text/plain")
        return ApiResponse(message="document indexed", data=document.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/documents/samples", response_model=ApiResponse)
def load_sample_documents() -> ApiResponse:
    documents = rag_service.load_samples()
    return ApiResponse(message="sample documents indexed", data=[doc.model_dump() for doc in documents])


@router.get("/stats", response_model=ApiResponse)
def get_knowledge_stats() -> ApiResponse:
    return ApiResponse(data=rag_service.stats())


@router.get("/documents", response_model=ApiResponse)
def list_documents() -> ApiResponse:
    documents = rag_service.retriever.list_documents()
    return ApiResponse(data=[doc.model_dump() for doc in documents])


@router.get("/documents/{document_id}/chunks", response_model=ApiResponse)
def list_document_chunks(document_id: str) -> ApiResponse:
    chunks = rag_service.retriever.list_chunks(document_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="document not found or has no chunks")
    return ApiResponse(data=[chunk.model_dump() for chunk in chunks])


@router.delete("/documents/{document_id}", response_model=ApiResponse)
def delete_document(document_id: str) -> ApiResponse:
    deleted = rag_service.retriever.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="document not found")
    return ApiResponse(message="document deleted")


@router.delete("/documents", response_model=ApiResponse)
def clear_documents() -> ApiResponse:
    rag_service.clear()
    return ApiResponse(message="knowledge base cleared")
