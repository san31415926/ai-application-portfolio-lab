import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

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
            show_thinking=request.show_thinking,
            chat_model=request.chat_model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/query/stream")
def stream_query_knowledge_base(request: QueryRequest) -> StreamingResponse:
    try:
        events = rag_service.stream_query(
            request.query,
            top_k=request.top_k,
            min_score=request.min_score,
            show_thinking=request.show_thinking,
            chat_model=request.chat_model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    def event_stream():
        for event in events:
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
