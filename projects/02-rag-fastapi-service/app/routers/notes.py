from fastapi import APIRouter, HTTPException, Query

from app.schemas import ApiResponse, NoteCreate, NoteSearchRequest, NoteUpdate, WritingAssistRequest
from app.services.note_service import note_service


router = APIRouter(prefix="/api/v1", tags=["notebook"])


@router.post("/notes", response_model=ApiResponse)
def create_note(payload: NoteCreate) -> ApiResponse:
    note = note_service.create(payload)
    return ApiResponse(message="note created", data=note.model_dump())


@router.post("/notes/samples", response_model=ApiResponse)
def load_sample_notes() -> ApiResponse:
    notes = note_service.load_samples()
    return ApiResponse(message="sample notes loaded", data=[note.model_dump() for note in notes])


@router.get("/notes", response_model=ApiResponse)
def list_notes() -> ApiResponse:
    notes = note_service.list_notes()
    return ApiResponse(data=[note.model_dump() for note in notes])


@router.get("/notes/stats", response_model=ApiResponse)
def note_stats() -> ApiResponse:
    return ApiResponse(data=note_service.stats())


@router.post("/notes/search", response_model=ApiResponse)
def search_notes(payload: NoteSearchRequest) -> ApiResponse:
    notes = note_service.search(payload.query, top_k=payload.top_k)
    return ApiResponse(data=[note.model_dump() for note in notes])


@router.get("/notes/{note_id}", response_model=ApiResponse)
def get_note(note_id: str) -> ApiResponse:
    note = note_service.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    return ApiResponse(data=note.model_dump())


@router.patch("/notes/{note_id}", response_model=ApiResponse)
def update_note(note_id: str, payload: NoteUpdate) -> ApiResponse:
    note = note_service.update(note_id, payload)
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    return ApiResponse(message="note updated", data=note.model_dump())


@router.delete("/notes/{note_id}", response_model=ApiResponse)
def delete_note(note_id: str) -> ApiResponse:
    deleted = note_service.delete(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="note not found")
    return ApiResponse(message="note deleted")


@router.get("/notes/{note_id}/related", response_model=ApiResponse)
def related_sources(note_id: str, top_k: int = Query(default=4, ge=1, le=10)) -> ApiResponse:
    sources = note_service.related_sources(note_id, top_k=top_k)
    if sources is None:
        raise HTTPException(status_code=404, detail="note not found")
    return ApiResponse(data=[source.model_dump() for source in sources])


@router.post("/notes/{note_id}/assist", response_model=ApiResponse)
def assist_writing(note_id: str, payload: WritingAssistRequest) -> ApiResponse:
    result = note_service.assist(note_id, payload.mode)
    if result is None:
        raise HTTPException(status_code=404, detail="note not found")
    return ApiResponse(data=result.model_dump())


@router.get("/reviews/due", response_model=ApiResponse)
def due_reviews() -> ApiResponse:
    notes = note_service.due_reviews()
    return ApiResponse(data=[note.model_dump() for note in notes])


@router.post("/reviews/{note_id}/complete", response_model=ApiResponse)
def complete_review(note_id: str) -> ApiResponse:
    note = note_service.complete_review(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    return ApiResponse(message="review completed", data=note.model_dump())
