from pydantic import BaseModel, Field

from app.core.config import DEFAULT_MIN_SCORE


class ApiResponse(BaseModel):
    success: bool = True
    message: str = "ok"
    data: object | None = None


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    content_type: str
    character_count: int
    chunk_count: int


class ChunkInfo(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    chunk_index: int
    content: str


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=4, ge=1, le=10)
    min_score: float = Field(default=DEFAULT_MIN_SCORE, ge=0, le=1)
    chat_model: str | None = Field(
        default=None,
        max_length=120,
        pattern=r"^[A-Za-z0-9._:-]+$",
    )


class SourceChunk(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    chunk_index: int
    score: float
    content: str


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list[SourceChunk]
    hit_count: int
    refused: bool
    answer_backend: str = "extractive"
    answer_model: str | None = None


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    content: str = Field(..., min_length=1, max_length=8000)
    tags: list[str] = Field(default_factory=list)
    category: str = Field(default="未分类", max_length=40)


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    content: str | None = Field(default=None, min_length=1, max_length=8000)
    tags: list[str] | None = None
    category: str | None = Field(default=None, max_length=40)


class NoteInfo(BaseModel):
    note_id: str
    title: str
    content: str
    tags: list[str]
    category: str
    created_at: str
    updated_at: str
    review_count: int
    next_review_at: str


class NoteSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=300)
    top_k: int = Field(default=5, ge=1, le=20)


class WritingAssistRequest(BaseModel):
    mode: str = Field(default="summary", pattern="^(summary|continue|action_items|tags)$")


class WritingAssistResponse(BaseModel):
    mode: str
    result: str
    related_sources: list[SourceChunk]
