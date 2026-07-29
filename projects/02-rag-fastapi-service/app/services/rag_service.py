from __future__ import annotations

import re
from pathlib import Path

from app.core.config import DEFAULT_MIN_SCORE, DEFAULT_TOP_K, SAMPLE_DIR
from app.schemas import DocumentInfo, QueryResponse, SourceChunk
from app.services.answer_generator import create_answer_generator, list_installed_chat_models
from app.services.document_loader import read_document_path
from app.services.retriever import EmbeddingRetriever, tokenize


class RagService:
    def __init__(self) -> None:
        self.retriever = EmbeddingRetriever()
        self.answer_generator = create_answer_generator()

    def clear(self) -> None:
        self.retriever.clear()

    def add_text(
        self,
        filename: str,
        text: str,
        content_type: str = "text/plain",
        rebuild_index: bool = True,
    ) -> DocumentInfo:
        if not text.strip():
            raise ValueError("document text is empty")
        return self.retriever.add_document(
            filename=filename,
            text=text,
            content_type=content_type,
            rebuild_index=rebuild_index,
        )

    def load_samples(self) -> list[DocumentInfo]:
        loaded: list[DocumentInfo] = []
        indexed_filenames = {document.filename for document in self.retriever.list_documents()}
        for path in sorted(SAMPLE_DIR.glob("*")):
            if path.suffix.lower() not in {".md", ".txt", ".pdf"}:
                continue
            if path.name in indexed_filenames:
                continue
            text = read_document_path(path)
            loaded.append(
                self.add_text(
                    path.name,
                    text,
                    content_type=f"text/{path.suffix.lower().lstrip('.')}",
                    rebuild_index=False,
                )
            )
            indexed_filenames.add(path.name)
        if loaded:
            self.retriever.rebuild_index()
        return loaded

    def stats(self) -> dict[str, int | str | None]:
        stats = self.retriever.stats()
        stats.update(
            {
                "answer_backend": self.answer_generator.name if self.answer_generator else "extractive",
                "answer_model": self.answer_generator.model_name if self.answer_generator else None,
            }
        )
        return stats

    def chat_models(self) -> dict[str, object]:
        return {
            "models": list_installed_chat_models(),
            "default_model": self.answer_generator.model_name if self.answer_generator else None,
        }

    def query(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        min_score: float = DEFAULT_MIN_SCORE,
        chat_model: str | None = None,
    ) -> QueryResponse:
        sources = self.retriever.search(query, top_k=top_k)
        if not sources or sources[0].score < min_score:
            return QueryResponse(
                query=query,
                answer="未检索到足够相关的资料，服务已拒答。请上传更相关的文档后再查询。",
                sources=sources,
                hit_count=len(sources),
                refused=True,
            )

        answer = ""
        answer_backend = "extractive"
        answer_model = None
        generator = self.answer_generator
        if generator is not None and chat_model:
            available_models = {item["name"] for item in list_installed_chat_models()}
            if chat_model not in available_models:
                raise ValueError(f"chat model is not installed: {chat_model}")
            generator = create_answer_generator(chat_model)
        if generator is not None:
            try:
                answer = generator.generate(query, sources[:1])
                answer_backend = generator.name
                answer_model = generator.model_name
            except RuntimeError:
                answer = ""
        if not answer:
            answer = self._compose_answer(query, sources)
        return QueryResponse(
            query=query,
            answer=answer,
            sources=sources,
            hit_count=len(sources),
            refused=False,
            answer_backend=answer_backend,
            answer_model=answer_model,
        )

    @staticmethod
    def _compose_answer(query: str, sources: list[SourceChunk]) -> str:
        query_terms = set(tokenize(query))
        ranked_sentences: list[tuple[int, float, int, str]] = []
        order = 0

        for source in sources:
            raw_sentences = [part.strip() for part in re.split(r"(?<=[。！？.!?])\s+|\n+", source.content) if part.strip()]
            for raw_sentence in raw_sentences:
                if raw_sentence.startswith("#"):
                    continue
                sentence = re.sub(r"^[-*]\s+", "", raw_sentence).strip()
                if not sentence:
                    continue
                sentence_terms = set(tokenize(sentence))
                overlap = len(query_terms.intersection(sentence_terms))
                if overlap:
                    ranked_sentences.append((overlap, source.score, order, sentence))
                    order += 1

        ranked_sentences.sort(key=lambda item: (-item[0], -item[1], item[2]))
        selected_sentences = [item[3] for item in ranked_sentences[:4]]

        if not selected_sentences:
            selected_sentences = [source.content[:180].strip() for source in sources[:2]]

        source_refs = "；".join(
            f"{source.filename} 第 {source.chunk_index} 段" for source in sources[:3]
        )
        return " ".join(selected_sentences) + f"\n\n来源：{source_refs}"


rag_service = RagService()
