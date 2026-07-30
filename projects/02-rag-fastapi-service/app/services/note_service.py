from __future__ import annotations

import re
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from app.core.config import SAMPLE_DIR
from app.schemas import NoteCreate, NoteInfo, NoteUpdate, SourceChunk, WritingAssistResponse
from app.services.rag_service import rag_service
from app.services.retriever import tokenize


REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]


@dataclass
class NoteRecord:
    note_id: str
    title: str
    content: str
    tags: list[str]
    category: str
    created_at: datetime
    updated_at: datetime
    review_count: int = 0
    next_review_at: datetime = field(default_factory=lambda: utc_now() + timedelta(days=1))


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def clean_tags(tags: list[str]) -> list[str]:
    cleaned: list[str] = []
    for tag in tags:
        value = tag.strip().strip("#")
        if value and value not in cleaned:
            cleaned.append(value[:24])
    return cleaned[:8]


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[。！？.!?])\s+|\n+", text) if part.strip()]


def sample_category(sample_number: int) -> str:
    if sample_number <= 100:
        return "生活百科"
    if sample_number <= 130:
        return "Python 与 FastAPI"
    if sample_number <= 143:
        return "C 语言与算法"
    if sample_number <= 150:
        return "SQL 数据库"
    if sample_number <= 160:
        return "Git、Linux 与 Docker"
    if sample_number <= 170:
        return "前端开发"
    if sample_number <= 178:
        return "测试与服务工程"
    if sample_number <= 186:
        return "数据分析"
    return "RAG 与本地 AI"


def sample_note_payload(path) -> NoteCreate:
    raw_text = path.read_text(encoding="utf-8").strip()
    first_line, separator, remaining = raw_text.partition("\n")
    title = first_line.removeprefix("#").strip() or path.stem
    content = (remaining if separator else raw_text).strip()
    number = int(path.stem.split("_")[1])
    category = sample_category(number)
    tags = clean_tags([category, title, "教程笔记", path.stem])
    return NoteCreate(
        title=title[:120],
        content=(content or title)[:8000],
        tags=tags,
        category=category,
    )


class NoteService:
    def __init__(self) -> None:
        self.notes: dict[str, NoteRecord] = {}
        self._samples_loaded = False

    def clear(self) -> None:
        self.notes.clear()
        self._samples_loaded = False

    def create(self, payload: NoteCreate) -> NoteInfo:
        now = utc_now()
        note = NoteRecord(
            note_id=uuid.uuid4().hex[:12],
            title=payload.title.strip(),
            content=payload.content.strip(),
            tags=clean_tags(payload.tags),
            category=(payload.category or "未分类").strip()[:40],
            created_at=now,
            updated_at=now,
            next_review_at=now + timedelta(days=1),
        )
        self.notes[note.note_id] = note
        return self._to_info(note)

    def load_samples(self) -> list[NoteInfo]:
        if self._samples_loaded:
            return []
        samples = [
            NoteCreate(
                title="C 语言变量入门笔记",
                category="编程学习",
                tags=["C语言", "变量", "编程基础"],
                content=(
                    "变量是给数据起名字的一种方式。学习 C 语言时，要先理解 int、double、char "
                    "这些基础类型，再练习用 printf 输出变量。"
                ),
            ),
            NoteCreate(
                title="番茄炒蛋复盘",
                category="做菜练习",
                tags=["做菜", "番茄炒蛋", "火候"],
                content=(
                    "番茄炒蛋的关键是鸡蛋不要炒太老，番茄要先炒出汁再放鸡蛋。"
                    "盐可以分两次放，糖只用来平衡酸味。"
                ),
            ),
            NoteCreate(
                title="学习教程库项目定位",
                category="项目设计",
                tags=["RAG", "Notebook", "教程库"],
                content=(
                    "项目目标是把各种教程资料做成个人学习知识库：用户能查询 C 语言、做菜、Python、"
                    "Excel 等主题，写学习笔记，并查看相关来源片段。"
                ),
            ),
            NoteCreate(
                title="Excel 透视表练习",
                category="办公技能",
                tags=["Excel", "透视表", "数据分析"],
                content=(
                    "透视表适合按分类快速汇总数据。练习时可以准备订单表，按城市统计销售额，"
                    "再按月份统计订单数量。"
                ),
            ),
            NoteCreate(
                title="英语听力训练计划",
                category="语言学习",
                tags=["英语", "听力", "复述"],
                content=(
                    "听力训练分为精听和泛听。精听要反复听一句话并写下来，泛听重在保持输入量。"
                    "口语可以从 30 秒材料复述开始。"
                ),
            ),
        ]
        samples.extend(
            sample_note_payload(path)
            for path in sorted(SAMPLE_DIR.glob("kb_*.md"))
        )
        created = [self.create(sample) for sample in samples]
        for note_info in created[:2]:
            self.notes[note_info.note_id].next_review_at = utc_now() - timedelta(minutes=1)
        self._samples_loaded = True
        return [self._to_info(self.notes[note.note_id]) for note in created]

    def list_notes(self) -> list[NoteInfo]:
        return [
            self._to_info(note)
            for note in sorted(self.notes.values(), key=lambda item: item.updated_at, reverse=True)
        ]

    def get(self, note_id: str) -> NoteInfo | None:
        note = self.notes.get(note_id)
        return self._to_info(note) if note else None

    def update(self, note_id: str, payload: NoteUpdate) -> NoteInfo | None:
        note = self.notes.get(note_id)
        if note is None:
            return None
        if payload.title is not None:
            note.title = payload.title.strip()
        if payload.content is not None:
            note.content = payload.content.strip()
        if payload.tags is not None:
            note.tags = clean_tags(payload.tags)
        if payload.category is not None:
            note.category = (payload.category or "未分类").strip()[:40]
        note.updated_at = utc_now()
        return self._to_info(note)

    def delete(self, note_id: str) -> bool:
        if note_id not in self.notes:
            return False
        del self.notes[note_id]
        return True

    def search(self, query: str, top_k: int = 5) -> list[NoteInfo]:
        query_tokens = Counter(tokenize(query))
        if not query_tokens:
            return []
        ranked: list[tuple[float, datetime, NoteRecord]] = []
        for note in self.notes.values():
            note_text = f"{note.title}\n{note.category}\n{' '.join(note.tags)}\n{note.content}"
            note_tokens = Counter(tokenize(note_text))
            overlap = sum(min(count, note_tokens.get(term, 0)) for term, count in query_tokens.items())
            if overlap <= 0:
                continue
            score = overlap / max(1, sum(query_tokens.values()))
            ranked.append((score, note.updated_at, note))
        ranked.sort(key=lambda item: (-item[0], item[1]), reverse=False)
        return [self._to_info(note) for _, _, note in ranked[:top_k]]

    def related_sources(self, note_id: str, top_k: int = 4) -> list[SourceChunk] | None:
        note = self.notes.get(note_id)
        if note is None:
            return None
        query = f"{note.title}\n{' '.join(note.tags)}\n{note.content[:1200]}"
        return rag_service.retriever.search(query, top_k=top_k)

    def assist(
        self,
        note_id: str,
        mode: str,
        chat_model: str | None = None,
    ) -> WritingAssistResponse | None:
        note = self.notes.get(note_id)
        if note is None:
            return None
        sources = self.related_sources(note_id, top_k=3) or []
        model_result, answer_model = self._assist_with_model(note, mode, sources, chat_model)
        answer_backend = "ollama" if model_result else "extractive"
        result = model_result
        if result is None:
            result = self._fallback_assist(note, mode, sources)
        return WritingAssistResponse(
            mode=mode,
            result=result,
            related_sources=sources,
            answer_backend=answer_backend,
            answer_model=answer_model,
        )

    def _assist_with_model(
        self,
        note: NoteRecord,
        mode: str,
        sources: list[SourceChunk],
        chat_model: str | None = None,
    ) -> tuple[str | None, str | None]:
        try:
            generator = rag_service._select_generator(chat_model)
        except ValueError:
            return None, None
        generate = getattr(generator, "generate_writing_assist", None) if generator else None
        if generate is None:
            return None, None
        try:
            return generate(mode, note.title, note.content, sources), generator.model_name
        except (RuntimeError, AttributeError):
            return None, None

    def _fallback_assist(self, note: NoteRecord, mode: str, sources: list[SourceChunk]) -> str:
        if mode == "summary":
            return self._summary(note, sources)
        elif mode == "continue":
            return self._continue(note, sources)
        elif mode == "action_items":
            return self._action_items(note, sources)
        else:
            return self._tags(note, sources)

    def due_reviews(self) -> list[NoteInfo]:
        now = utc_now()
        return [
            self._to_info(note)
            for note in sorted(self.notes.values(), key=lambda item: item.next_review_at)
            if note.next_review_at <= now
        ]

    def complete_review(self, note_id: str) -> NoteInfo | None:
        note = self.notes.get(note_id)
        if note is None:
            return None
        interval = REVIEW_INTERVALS[min(note.review_count, len(REVIEW_INTERVALS) - 1)]
        note.review_count += 1
        note.next_review_at = utc_now() + timedelta(days=interval)
        note.updated_at = utc_now()
        return self._to_info(note)

    def stats(self) -> dict[str, int]:
        return {
            "note_count": len(self.notes),
            "tag_count": len({tag for note in self.notes.values() for tag in note.tags}),
            "review_due_count": len(self.due_reviews()),
            "character_count": sum(len(note.content) for note in self.notes.values()),
        }

    def _summary(self, note: NoteRecord, sources: list[SourceChunk]) -> str:
        sentences = split_sentences(note.content)
        selected = sentences[:2] if sentences else [note.content[:160]]
        if sources:
            selected.append(f"相关资料主要来自 {sources[0].filename} 第 {sources[0].chunk_index} 段。")
        return "\n".join(f"- {sentence}" for sentence in selected)

    def _continue(self, note: NoteRecord, sources: list[SourceChunk]) -> str:
        source_hint = ""
        if sources:
            source_hint = f"可继续结合 `{sources[0].filename}` 的来源片段，补充证据和边界条件。"
        return (
            "可以继续写：\n"
            f"1. 这个问题的核心判断是：{note.title}。\n"
            "2. 需要把结论、适用条件、例外情况和下一步动作分开写清楚。\n"
            f"3. {source_hint or '如果没有来源证据，应该标记为待确认，而不是直接下结论。'}"
        )

    def _action_items(self, note: NoteRecord, sources: list[SourceChunk]) -> str:
        items = [
            "补充一个真实查询示例，用来证明笔记能和知识库关联。",
            "检查回答中是否包含来源文件名和 chunk 编号。",
            "把这条笔记整理成可以面试讲述的输入、处理、输出结构。",
        ]
        if sources:
            items.append(f"复核 `{sources[0].filename}` 中是否还有可加入笔记的关键规则。")
        return "\n".join(f"- {item}" for item in items)

    def _tags(self, note: NoteRecord, sources: list[SourceChunk]) -> str:
        terms = Counter(tokenize(f"{note.title} {' '.join(note.tags)} {note.content}"))
        for source in sources:
            terms.update(tokenize(source.content[:400]))
        candidates = [term for term, _ in terms.most_common(12) if len(term) >= 2]
        return "、".join(candidates[:8]) or "未识别到稳定标签"

    @staticmethod
    def _to_info(note: NoteRecord) -> NoteInfo:
        return NoteInfo(
            note_id=note.note_id,
            title=note.title,
            content=note.content,
            tags=note.tags,
            category=note.category,
            created_at=note.created_at.isoformat(),
            updated_at=note.updated_at.isoformat(),
            review_count=note.review_count,
            next_review_at=note.next_review_at.isoformat(),
        )


note_service = NoteService()
