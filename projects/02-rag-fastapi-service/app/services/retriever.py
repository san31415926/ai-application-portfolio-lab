from __future__ import annotations

import json
import math
import re
import uuid
from collections import Counter
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import (
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_TIMEOUT,
    RAG_EMBEDDING_BACKEND,
    RAG_LOCAL_EMBEDDING_MODEL,
)
from app.schemas import ChunkInfo, DocumentInfo, SourceChunk
from app.services.text_splitter import split_text


Vector = dict[str, float] | list[float]


TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.\-]*|\d+(?:\.\d+)?|[\u4e00-\u9fff]+")

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "how",
    "is",
    "of",
    "or",
    "the",
    "to",
    "what",
    "when",
    "which",
    "with",
    "一个",
    "什么",
    "哪些",
    "如何",
    "我们",
    "这个",
    "这些",
    "怎么",
    "是什么",
    "是什",
}


@dataclass
class DocumentRecord:
    document_id: str
    filename: str
    content_type: str
    text: str


@dataclass
class ChunkRecord:
    chunk_id: str
    document_id: str
    filename: str
    chunk_index: int
    content: str


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in TOKEN_RE.findall(text.lower()):
        if raw in STOPWORDS:
            continue
        if re.fullmatch(r"[\u4e00-\u9fff]+", raw):
            if len(raw) <= 4:
                tokens.append(raw)
            for size in (2, 3):
                for start in range(0, len(raw) - size + 1):
                    ngram = raw[start : start + size]
                    if ngram not in STOPWORDS:
                        tokens.append(ngram)
            continue
        tokens.append(raw)
        if raw.endswith("s") and len(raw) > 4:
            tokens.append(raw[:-1])
    return tokens


class LocalSparseEmbeddingModel:
    """Offline sparse embedding model for a runnable local RAG demo."""

    name = "local-sparse"
    model_name = "local-sparse"

    def __init__(self, fallback_reason: str | None = None) -> None:
        self.fallback_reason = fallback_reason

    def embed_query(self, text: str) -> Vector:
        return self._embed_text(text)

    def embed_documents(self, texts: list[str]) -> list[Vector]:
        return [self._embed_text(text) for text in texts]

    def _embed_text(self, text: str) -> Vector:
        tokens = Counter(tokenize(text))
        vector: dict[str, float] = {}
        for token, count in tokens.items():
            vector[token] = math.log1p(count)
        return vector


class OllamaEmbeddingModel:
    """Embedding model served by a local Ollama process."""

    name = "ollama"

    def __init__(
        self,
        model_name: str = RAG_LOCAL_EMBEDDING_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        timeout: float = OLLAMA_EMBED_TIMEOUT,
    ) -> None:
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def embed_query(self, text: str) -> Vector:
        return self._embed_many([text])[0]

    def embed_documents(self, texts: list[str]) -> list[Vector]:
        return self._embed_many(texts)

    def _embed_many(self, texts: list[str]) -> list[Vector]:
        if not texts:
            return []
        body = json.dumps({"model": self.model_name, "input": texts}).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/embed",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(f"Ollama Embedding 不可用：{exc}") from exc

        embeddings = payload.get("embeddings")
        if embeddings is None and "embedding" in payload:
            embeddings = [payload["embedding"]]
        if not isinstance(embeddings, list) or len(embeddings) != len(texts):
            raise RuntimeError("Ollama 返回了无法识别的 Embedding 响应")
        return [[float(value) for value in embedding] for embedding in embeddings]


def create_embedding_model() -> LocalSparseEmbeddingModel | OllamaEmbeddingModel:
    if RAG_EMBEDDING_BACKEND in {"ollama", "local-ollama"}:
        return OllamaEmbeddingModel()
    return LocalSparseEmbeddingModel()


class EmbeddingRetriever:
    """In-memory vector retriever with the same flow as LangChain Embeddings + Chroma."""

    def __init__(self) -> None:
        self.documents: dict[str, DocumentRecord] = {}
        self.chunks: list[ChunkRecord] = []
        self.embedding_model = create_embedding_model()
        self._vectors: list[Vector] = []
        self._norms: list[float] = []

    def clear(self) -> None:
        self.documents.clear()
        self.chunks.clear()
        self._rebuild_index()

    def add_document(
        self,
        filename: str,
        text: str,
        content_type: str = "text/plain",
        rebuild_index: bool = True,
    ) -> DocumentInfo:
        document_id = uuid.uuid4().hex[:12]
        record = DocumentRecord(document_id=document_id, filename=filename, content_type=content_type, text=text)
        self.documents[document_id] = record

        pieces = split_text(text)
        for index, piece in enumerate(pieces, start=1):
            self.chunks.append(
                ChunkRecord(
                    chunk_id=f"{document_id}-{index}",
                    document_id=document_id,
                    filename=filename,
                    chunk_index=index,
                    content=piece,
                )
            )
        if rebuild_index:
            self._rebuild_index()
        return self._document_info(record)

    def rebuild_index(self) -> None:
        self._rebuild_index()

    def delete_document(self, document_id: str) -> bool:
        if document_id not in self.documents:
            return False
        del self.documents[document_id]
        self.chunks = [chunk for chunk in self.chunks if chunk.document_id != document_id]
        self._rebuild_index()
        return True

    def list_documents(self) -> list[DocumentInfo]:
        return [self._document_info(record) for record in self.documents.values()]

    def stats(self) -> dict[str, int | str]:
        return {
            "document_count": len(self.documents),
            "chunk_count": len(self.chunks),
            "character_count": sum(len(record.text) for record in self.documents.values()),
            "embedding_backend": self.embedding_model.name,
            "embedding_model": self.embedding_model.model_name,
        }

    def list_chunks(self, document_id: str) -> list[ChunkInfo]:
        return [
            ChunkInfo(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                filename=chunk.filename,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
            )
            for chunk in self.chunks
            if chunk.document_id == document_id
        ]

    def search(self, query: str, top_k: int) -> list[SourceChunk]:
        query_vector = self._embed_query(query)
        query_norm = self._norm(query_vector)
        if not query_vector or query_norm == 0:
            return []

        results: list[SourceChunk] = []
        for chunk, vector, norm in zip(self.chunks, self._vectors, self._norms):
            if norm == 0:
                continue
            score = self._cosine_similarity(query_vector, query_norm, vector, norm)
            if score <= 0:
                continue
            results.append(
                SourceChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    filename=chunk.filename,
                    chunk_index=chunk.chunk_index,
                    score=round(score, 4),
                    content=chunk.content,
                )
            )
        return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]

    def _document_info(self, record: DocumentRecord) -> DocumentInfo:
        chunk_count = sum(1 for chunk in self.chunks if chunk.document_id == record.document_id)
        return DocumentInfo(
            document_id=record.document_id,
            filename=record.filename,
            content_type=record.content_type,
            character_count=len(record.text),
            chunk_count=chunk_count,
        )

    def _rebuild_index(self) -> None:
        self._vectors = self._embed_documents([chunk.content for chunk in self.chunks])
        self._norms = [self._norm(vector) for vector in self._vectors]

    def _embed_query(self, query: str) -> Vector:
        try:
            return self.embedding_model.embed_query(query)
        except RuntimeError as exc:
            self._switch_to_sparse(exc)
            return self.embedding_model.embed_query(query)

    def _embed_documents(self, texts: list[str]) -> list[Vector]:
        try:
            return self.embedding_model.embed_documents(texts)
        except RuntimeError as exc:
            self._switch_to_sparse(exc)
            return self.embedding_model.embed_documents(texts)

    def _switch_to_sparse(self, exc: RuntimeError) -> None:
        if isinstance(self.embedding_model, LocalSparseEmbeddingModel):
            raise exc
        self.embedding_model = LocalSparseEmbeddingModel(fallback_reason=str(exc))
        self._vectors = self.embedding_model.embed_documents([chunk.content for chunk in self.chunks])
        self._norms = [self._norm(vector) for vector in self._vectors]

    @staticmethod
    def _norm(vector: Vector) -> float:
        values = vector.values() if isinstance(vector, dict) else vector
        return math.sqrt(sum(value * value for value in values))

    @staticmethod
    def _cosine_similarity(
        query_vector: Vector,
        query_norm: float,
        chunk_vector: Vector,
        chunk_norm: float,
    ) -> float:
        if isinstance(query_vector, dict) and isinstance(chunk_vector, dict):
            dot = sum(value * chunk_vector.get(term, 0.0) for term, value in query_vector.items())
        elif isinstance(query_vector, list) and isinstance(chunk_vector, list):
            dot = sum(query_value * chunk_value for query_value, chunk_value in zip(query_vector, chunk_vector))
        else:
            return 0.0
        return dot / (query_norm * chunk_norm)
