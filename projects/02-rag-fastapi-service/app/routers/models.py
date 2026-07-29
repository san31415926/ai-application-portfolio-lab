from fastapi import APIRouter

from app.schemas import ApiResponse
from app.services.rag_service import rag_service


router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.get("", response_model=ApiResponse)
def list_chat_models() -> ApiResponse:
    return ApiResponse(data=rag_service.chat_models())
