from __future__ import annotations

import argparse
import math
import re
import textwrap
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_PATHS = [
    PROJECT_ROOT / "samples" / "source" / "ai_application_engineer_jd.md",
    PROJECT_ROOT / "samples" / "source" / "rag_learning_notes.md",
    PROJECT_ROOT / "projects" / "01-chat-with-pdf" / "README.md",
    PROJECT_ROOT / "projects" / "01-chat-with-pdf" / "notes.md",
]

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.\-]*|\d+(?:\.\d+)?|[\u4e00-\u9fff]+")
ENGLISH_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "how",
    "is",
    "it",
    "of",
    "or",
    "should",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "which",
    "with",
}
CHINESE_STOPWORDS = {
    "一个",
    "什么",
    "他们",
    "以及",
    "你的",
    "哪些",
    "如何",
    "我们",
    "我的",
    "是否",
    "这个",
    "这些",
    "那个",
    "怎么",
}

QUERY_EXPANSIONS = {
    "技能": "skills required requirements python langchain rag embeddings vector database prompts api git debug",
    "要求": "requirements required skills responsibilities must have nice to have",
    "岗位": "role job description responsibilities skills",
    "简历": "resume portfolio project bullets impact evidence",
    "项目": "project portfolio demo prototype build resume",
    "作品集": "portfolio github readme demo architecture",
    "学习": "learn beginner roadmap first chunking embeddings vector store",
    "先学": "beginner learning advice first roadmap",
    "面试": "interview questions explain evaluate hallucination",
    "幻觉": "hallucination grounded sources refuse evidence",
    "引用": "sources cite snippets grounded answer",
    "rag": "retrieval augmented generation chunking embeddings vector store retriever prompts sources",
}

SKILL_KEYWORDS = {
    "Python": ["python"],
    "RAG": ["rag", "retrieval", "augmented", "generation"],
    "文档解析": ["pdf", "markdown", "documents", "load", "parsing", "读取"],
    "文本切分": ["chunk", "chunking", "split"],
    "向量表示": ["embedding", "embeddings", "vectors"],
    "向量数据库": ["vector", "chroma", "faiss", "pinecone", "database"],
    "提示词设计": ["prompt", "prompts", "grounded"],
    "Agent 工具调用": ["agent", "tool", "tools", "workflows"],
    "网页演示": ["streamlit", "web", "demo"],
    "评估与防幻觉": ["evaluate", "evaluation", "hallucination", "relevance", "faithfulness", "refuse"],
    "工程化文档": ["documentation", "readme", "git", "environment", "teammates"],
}


@dataclass(frozen=True)
class Document:
    source: Path
    text: str


@dataclass(frozen=True)
class Chunk:
    id: str
    source: Path
    index: int
    text: str


@dataclass(frozen=True)
class RetrievalResult:
    chunk: Chunk
    score: float
    matched_terms: tuple[str, ...]


def read_pdf(path: Path) -> str:
    reader = PdfReader(path)
    page_texts: list[str] = []

    for page in reader.pages:
        page_texts.append(page.extract_text() or "")

    return "\n".join(page_texts)


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return read_pdf(path)

    return path.read_text(encoding="utf-8")


def load_documents(paths: Iterable[Path]) -> list[Document]:
    documents: list[Document] = []

    for path in paths:
        resolved = path if path.is_absolute() else PROJECT_ROOT / path
        if not resolved.exists():
            raise FileNotFoundError(f"找不到来源文件：{resolved}")
        documents.append(Document(source=resolved, text=read_text(resolved)))

    return documents


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_chunks(text: str, source: Path, chunk_size: int = 900, overlap: int = 120) -> list[Chunk]:
    clean_text = normalize_text(text)
    if not clean_text:
        return []

    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", clean_text) if paragraph.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if current:
                chunks.append(current.strip())
                current = ""
            step = max(1, chunk_size - overlap)
            for start in range(0, len(paragraph), step):
                piece = paragraph[start : start + chunk_size].strip()
                if piece:
                    chunks.append(piece)
            continue

        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            chunks.append(current.strip())
            suffix = current[-overlap:].strip() if overlap and current else ""
            current = f"{suffix}\n\n{paragraph}".strip() if suffix else paragraph

    if current:
        chunks.append(current.strip())

    return [
        Chunk(id=f"{source.name}#{index + 1}", source=source, index=index + 1, text=chunk)
        for index, chunk in enumerate(chunks)
    ]


def tokenize(text: str) -> list[str]:
    raw_tokens = [token.lower() for token in TOKEN_RE.findall(text)]
    normalized: list[str] = []

    for token in raw_tokens:
        if token in ENGLISH_STOPWORDS or token in CHINESE_STOPWORDS:
            continue
        if re.fullmatch(r"[\u4e00-\u9fff]+", token):
            if len(token) <= 4 and token not in CHINESE_STOPWORDS:
                normalized.append(token)
            for size in (2, 3):
                for start in range(0, len(token) - size + 1):
                    ngram = token[start : start + size]
                    if ngram not in CHINESE_STOPWORDS:
                        normalized.append(ngram)
            continue
        normalized.append(token)
        if token.endswith("s") and len(token) > 4:
            normalized.append(token[:-1])

    return normalized


def expand_query(query: str) -> str:
    additions: list[str] = []
    lowered = query.lower()

    for trigger, expansion in QUERY_EXPANSIONS.items():
        if trigger in query or trigger in lowered:
            additions.append(expansion)

    return f"{query} {' '.join(additions)}".strip()


class KnowledgeBase:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self.chunk_tokens = [Counter(tokenize(chunk.text)) for chunk in chunks]
        self.idf = self._build_idf(self.chunk_tokens)
        self.chunk_vectors = [self._vectorize(tokens) for tokens in self.chunk_tokens]
        self.chunk_norms = [self._norm(vector) for vector in self.chunk_vectors]

    @classmethod
    def from_documents(
        cls,
        documents: list[Document],
        chunk_size: int = 900,
        overlap: int = 120,
    ) -> "KnowledgeBase":
        chunks: list[Chunk] = []
        for document in documents:
            chunks.extend(split_into_chunks(document.text, document.source, chunk_size, overlap))
        return cls(chunks)

    @classmethod
    def from_paths(
        cls,
        paths: Iterable[Path],
        chunk_size: int = 900,
        overlap: int = 120,
    ) -> "KnowledgeBase":
        return cls.from_documents(load_documents(paths), chunk_size, overlap)

    def retrieve(self, query: str, top_k: int = 4) -> list[RetrievalResult]:
        expanded_query = expand_query(query)
        query_tokens = Counter(tokenize(expanded_query))
        query_vector = self._vectorize(query_tokens)
        query_norm = self._norm(query_vector)
        if not query_vector or query_norm == 0:
            return []

        results: list[RetrievalResult] = []
        query_terms = set(query_vector)

        for chunk, vector, norm in zip(self.chunks, self.chunk_vectors, self.chunk_norms):
            if norm == 0:
                continue
            score = self._cosine_similarity(query_vector, query_norm, vector, norm)
            if score <= 0:
                continue
            matched_terms = tuple(sorted(query_terms.intersection(vector.keys()))[:12])
            results.append(RetrievalResult(chunk=chunk, score=score, matched_terms=matched_terms))

        return sorted(results, key=lambda result: result.score, reverse=True)[:top_k]

    @staticmethod
    def _build_idf(chunk_tokens: list[Counter[str]]) -> dict[str, float]:
        document_count = max(1, len(chunk_tokens))
        document_frequency: Counter[str] = Counter()

        for tokens in chunk_tokens:
            document_frequency.update(tokens.keys())

        return {
            term: math.log((document_count + 1) / (frequency + 1)) + 1
            for term, frequency in document_frequency.items()
        }

    def _vectorize(self, tokens: Counter[str]) -> dict[str, float]:
        return {term: count * self.idf.get(term, 1.0) for term, count in tokens.items()}

    @staticmethod
    def _norm(vector: dict[str, float]) -> float:
        return math.sqrt(sum(value * value for value in vector.values()))

    @staticmethod
    def _cosine_similarity(
        query_vector: dict[str, float],
        query_norm: float,
        chunk_vector: dict[str, float],
        chunk_norm: float,
    ) -> float:
        dot = sum(value * chunk_vector.get(term, 0.0) for term, value in query_vector.items())
        return dot / (query_norm * chunk_norm)


def relative_source(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def detect_skills(results: list[RetrievalResult]) -> list[str]:
    combined = " ".join(result.chunk.text.lower() for result in results)
    found: list[str] = []

    for skill, keywords in SKILL_KEYWORDS.items():
        if any(keyword.lower() in combined for keyword in keywords):
            found.append(skill)

    return found


def citation_line(result: RetrievalResult, number: int) -> str:
    return f"[{number}] {relative_source(result.chunk.source)} chunk {result.chunk.index}"


def format_snippet(text: str, width: int = 260) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return textwrap.shorten(compact, width=width, placeholder="...")


def classify_intent(question: str) -> str:
    lowered = question.lower()
    if any(keyword in question for keyword in ["技能", "要求", "岗位"]) or "skill" in lowered:
        return "skills"
    if any(keyword in question for keyword in ["先学", "学习", "路线"]) or "learn" in lowered:
        return "learning"
    if any(keyword in question for keyword in ["简历", "作品集", "项目亮点"]) or "resume" in lowered:
        return "resume"
    if "面试" in question or "interview" in lowered:
        return "interview"
    return "generic"


def answer_question(question: str, results: list[RetrievalResult], min_score: float = 0.05) -> str:
    if not results or results[0].score < min_score:
        return (
            "当前知识库没有足够证据，不能安全回答这个问题。\n"
            "请补充更多来源文档，或提一个更接近岗位 JD、RAG 学习笔记、项目文档的问题。"
        )

    intent = classify_intent(question)
    skills = detect_skills(results)
    citations = [citation_line(result, index + 1) for index, result in enumerate(results)]

    lines: list[str] = []
    lines.append(f"问题：{question}")
    lines.append("")

    if intent == "skills":
        lines.append("回答：")
        lines.append("这个岗位强调的是把大模型、数据、工具和用户界面连接成可用应用，而不是从零训练基础模型。")
        if skills:
            lines.append("从来源材料中能支撑的技能方向：" + "、".join(skills[:8]) + "。")
        lines.append("简历里要用一个可运行的文档问答/RAG 项目证明这些能力，并展示来源引用、拒答和清晰文档。")
    elif intent == "learning":
        lines.append("回答：")
        lines.append("学习顺序建议按 RAG 链路推进：读取文档、切分 chunk、检索相关上下文，再生成有证据支撑的回答。")
        lines.append("对这个仓库来说，下一步是把轻量检索升级为 embeddings + 向量数据库，并补充可截图的网页演示。")
    elif intent == "resume":
        lines.append("回答：")
        lines.append("这个项目适合包装成“AI 岗位 JD 知识库”：读取岗位 JD 和学习笔记，检索相关来源片段，回答技能差距、学习路径和面试准备问题。")
        lines.append("简历 bullet 草稿：基于 Python 实现本地 RAG 风格岗位知识库，支持读取 PDF/Markdown、文本切分、相关片段检索和来源引用，用于 AI 应用工程师岗位准备。")
    elif intent == "interview":
        lines.append("回答：")
        lines.append("面试时要能解释：RAG 为什么能降低幻觉、为什么要切 chunk、如何判断检索质量，以及证据不足时系统为什么要拒答。")
        lines.append("推荐讲法：输入文档 -> 切分 chunk -> 检索相关片段 -> 基于证据回答 -> 展示来源 -> 证据不足时拒答。")
    else:
        lines.append("回答：")
        lines.append("根据检索到的来源，这个项目的重点是把文档变成可检索知识库，并用可见证据回答求职相关问题。")

    lines.append("")
    lines.append("来源：")
    for index, result in enumerate(results, start=1):
        lines.append(f"{citation_line(result, index)} | score={result.score:.3f}")
        lines.append(f"  {format_snippet(result.chunk.text)}")

    lines.append("")
    lines.append("命中词：")
    for index, result in enumerate(results, start=1):
        terms = ", ".join(result.matched_terms) if result.matched_terms else "无"
        lines.append(f"[{index}] {terms}")

    lines.append("")
    lines.append("引用位置：" + "; ".join(citations))
    return "\n".join(lines)


def parse_source_paths(values: list[str] | None) -> list[Path]:
    if not values:
        return DEFAULT_SOURCE_PATHS
    return [Path(value) for value in values]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="基于本地来源证据的 AI 岗位 JD 知识库演示。"
    )
    parser.add_argument(
        "question",
        nargs="?",
        default="这个岗位要求哪些技能？",
        help="要向本地知识库提问的问题。",
    )
    parser.add_argument(
        "--source",
        action="append",
        help="来源文件路径，可重复使用；默认读取示例 JD、RAG 笔记和项目文档。",
    )
    parser.add_argument("--top-k", type=int, default=4, help="返回的相关片段数量。")
    parser.add_argument("--chunk-size", type=int, default=900, help="每个片段的最大字符数。")
    parser.add_argument("--overlap", type=int, default=120, help="相邻片段之间重叠的字符数。")
    parser.add_argument("--show-index", action="store_true", help="回答前打印已建立索引的片段。")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    source_paths = parse_source_paths(args.source)
    documents = load_documents(source_paths)
    knowledge_base = KnowledgeBase.from_documents(documents, args.chunk_size, args.overlap)

    if args.show_index:
        print(f"已索引文档：{len(documents)}")
        print(f"已索引片段：{len(knowledge_base.chunks)}")
        for chunk in knowledge_base.chunks:
            print(f"- {chunk.id}：{relative_source(chunk.source)}（{len(chunk.text)} 个字符）")
        print()

    results = knowledge_base.retrieve(args.question, args.top_k)
    print(answer_question(args.question, results))


if __name__ == "__main__":
    main()
