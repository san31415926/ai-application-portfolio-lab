import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parents[2]
SAMPLE_DIR = PROJECT_DIR / "samples"
load_dotenv(PROJECT_DIR.parents[1] / ".env")

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf"}
DEFAULT_CHUNK_SIZE = 700
DEFAULT_CHUNK_OVERLAP = 120
DEFAULT_TOP_K = 4

RAG_EMBEDDING_BACKEND = os.getenv("RAG_EMBEDDING_BACKEND", "ollama").strip().lower()
RAG_LOCAL_EMBEDDING_MODEL = os.getenv("RAG_LOCAL_EMBEDDING_MODEL", "embeddinggemma:300m").strip()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_EMBED_TIMEOUT = float(os.getenv("OLLAMA_EMBED_TIMEOUT", "60"))

RAG_GENERATION_BACKEND = os.getenv("RAG_GENERATION_BACKEND", "ollama").strip().lower()
RAG_LOCAL_CHAT_MODEL = os.getenv("RAG_LOCAL_CHAT_MODEL", "qwen2.5:3b").strip()
OLLAMA_GENERATE_TIMEOUT = float(os.getenv("OLLAMA_GENERATE_TIMEOUT", "120"))
RAG_MAX_CONTEXT_CHARS = int(os.getenv("RAG_MAX_CONTEXT_CHARS", "6000"))
RAG_MAX_GENERATION_TOKENS = int(os.getenv("RAG_MAX_GENERATION_TOKENS", "2048"))
NOTE_DB_PATH = os.getenv(
    "NOTE_DB_PATH",
    str(PROJECT_DIR.parents[1] / "data" / "processed" / "learninghub_notes.sqlite"),
)

DEFAULT_MIN_SCORE = float(
    os.getenv(
        "RAG_MIN_SCORE",
        "0.2" if RAG_EMBEDDING_BACKEND in {"ollama", "local-ollama"} else "0.045",
    )
)
