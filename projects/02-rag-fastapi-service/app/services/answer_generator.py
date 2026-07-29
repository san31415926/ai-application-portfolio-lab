from __future__ import annotations

import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import (
    OLLAMA_BASE_URL,
    OLLAMA_GENERATE_TIMEOUT,
    RAG_GENERATION_BACKEND,
    RAG_LOCAL_CHAT_MODEL,
    RAG_MAX_CONTEXT_CHARS,
)
from app.schemas import SourceChunk


class OllamaAnswerGenerator:
    name = "ollama"

    def __init__(
        self,
        model_name: str = RAG_LOCAL_CHAT_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        timeout: float = OLLAMA_GENERATE_TIMEOUT,
    ) -> None:
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(self, query: str, sources: list[SourceChunk]) -> str:
        context = self._build_context(sources)
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是 LearningHub 的学习助理。严格遵守以下规则：只根据参考资料回答，"
                        "不得补充资料中没有的事实；直接回答问题，控制在 2 到 4 句话；"
                        "在相关结论后标注 [来源1] 这类编号；不要输出思考过程。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "/no_think\n"
                        "请直接输出给用户看的最终答案，不要分析问题，不要复述任务规则，"
                        "不要列出参考资料筛选过程。回答控制在 2 到 4 句话，并在相关结论后"
                        f"标注来源编号。\n\n问题：{query}\n\n参考资料：\n{context}"
                    ),
                },
            ],
            "stream": False,
            "think": False,
            "options": {"temperature": 0.1, "num_predict": 768},
            "keep_alive": "10m",
        }
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(f"Ollama 回答生成不可用：{exc}") from exc

        answer = result.get("message", {}).get("content", "").strip()
        if not answer:
            answer = result.get("response", "").strip()
        answer = self._extract_final_answer(answer)
        if not answer:
            raise RuntimeError("Ollama 没有返回最终答案")
        answer = re.sub(r"\s*来源\d+\s*$", "", answer).strip()
        if "[来源" not in answer:
            answer += "\n\n" + " ".join(f"[来源{index}]" for index in range(1, len(sources) + 1))
        return answer

    @staticmethod
    def _extract_final_answer(raw_answer: str) -> str:
        """Hide Qwen3 reasoning when an older Ollama template mixes it into content."""
        if not raw_answer:
            return ""
        markers = ("最终答案：", "最终答案:")
        marker_positions = [raw_answer.rfind(marker) for marker in markers]
        marker_position = max(marker_positions)
        if marker_position >= 0:
            marker = markers[marker_positions.index(marker_position)]
            candidate = raw_answer[marker_position + len(marker) :]
            candidate = re.split(r"\n\s*\n", candidate, maxsplit=1)[0]
            return candidate.strip().strip('"“”')
        if "<think>" in raw_answer or raw_answer.startswith(("首先", "我需要", "用户的问题")):
            return ""
        return re.sub(r"</?think>", "", raw_answer).strip()

    @staticmethod
    def _build_context(sources: list[SourceChunk]) -> str:
        sections: list[str] = []
        used_chars = 0
        for index, source in enumerate(sources, start=1):
            header = f"[来源{index}] {source.filename} 第 {source.chunk_index} 段"
            remaining = RAG_MAX_CONTEXT_CHARS - used_chars - len(header) - 2
            if remaining <= 0:
                break
            content = source.content[:remaining]
            sections.append(f"{header}\n{content}")
            used_chars += len(header) + len(content) + 2
        return "\n\n".join(sections)


def create_answer_generator(model_name: str | None = None) -> OllamaAnswerGenerator | None:
    if RAG_GENERATION_BACKEND in {"ollama", "local-ollama"}:
        return OllamaAnswerGenerator(model_name=model_name or RAG_LOCAL_CHAT_MODEL)
    return None


def list_installed_chat_models(base_url: str = OLLAMA_BASE_URL) -> list[dict[str, object]]:
    request = Request(
        f"{base_url.rstrip('/')}/api/tags",
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError):
        return []

    models: list[dict[str, object]] = []
    generation_capabilities = {"completion", "tools", "thinking"}
    for raw_model in payload.get("models", []):
        capabilities = [str(item) for item in raw_model.get("capabilities", [])]
        if capabilities and not generation_capabilities.intersection(capabilities):
            continue
        details = raw_model.get("details") or {}
        models.append(
            {
                "name": raw_model.get("name"),
                "size": raw_model.get("size", 0),
                "parameter_size": details.get("parameter_size"),
                "capabilities": capabilities,
            }
        )
    return models
