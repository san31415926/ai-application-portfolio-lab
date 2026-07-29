from fastapi import APIRouter


router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "rag-fastapi-service"}
