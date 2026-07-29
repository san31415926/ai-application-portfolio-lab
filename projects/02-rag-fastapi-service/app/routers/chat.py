from fastapi import APIRouter, HTTPException

from app.schemas import QueryRequest, QueryResponse
from app.services.rag_service import rag_service


router = APIRouter(prefix="/api/v1/chat", tags=["问答"])


@router.post("/query", response_model=QueryResponse)
def query_knowledge_base(request: QueryRequest) -> QueryResponse:
    try:
        return rag_service.query(
            request.query,
            top_k=request.top_k,
            min_score=request.min_score,
            chat_model=request.chat_model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
