# Decision Log

## 2026-07-27: Pivot Flagship To RAG Notebook Lite

- User preferred `RMA-MUN/RAGNotebook` as the target style for a resume project.
- Decision: keep the existing FastAPI RAG service as the base and upgrade it into a lightweight notebook product instead of copying the full upstream stack.
- Scope for MVP: knowledge upload, chunking, retrieval QA, source citations, note CRUD, note search, related source retrieval, deterministic writing assistance, and review scheduling.
- Deferred: React/Tiptap frontend, MySQL/Redis, real embeddings, ChromaDB, true LLM streaming, authentication, and deployment.
- Resume positioning: "reproduced and adapted a RAG Notebook-style prototype" rather than "built a production-grade system."

## 2026-07-28: Align Retrieval Story With Embeddings

- User said they had not studied earlier keyword-style retrieval much, but had seen LangChain Embeddings.
- Decision: rename and reshape the flagship retriever as `EmbeddingRetriever` with a local sparse embedding model, so the runnable demo follows the same high-level flow as LangChain Embeddings + vector search.
- Scope: keep the service offline and testable without API keys; generate vectors for chunks and queries, then rank by cosine similarity and return source chunks.
- Deferred: replace `LocalSparseEmbeddingModel` with LangChain `Embeddings`, add Chroma persistence, and add retrieval evaluation cases.
- Interview positioning: "I first used a local embedding-style implementation to understand and verify the RAG pipeline, then planned a LangChain + Chroma upgrade" rather than "I built a production vector database system."

## 2026-07-28: Add Ollama Local Embedding Model

- User wanted to run a small local model instead of only using the sparse embedding fallback.
- Decision: install Ollama locally and pull `embeddinggemma:300m`; connect `EmbeddingRetriever` to Ollama `/api/embed` by default.
- Scope: document chunks and user queries are embedded by Ollama, ranked with cosine similarity, and returned with source chunks; if Ollama is unavailable, the service falls back to `LocalSparseEmbeddingModel`.
- Validation: `embeddinggemma:300m` returned 768-dimensional embeddings; sample queries for C language variables and tomato scrambled eggs retrieved the expected source files, while an unrelated Mars treaty query refused with `RAG_MIN_SCORE=0.2`.
- Deferred: add Chroma persistence, retrieval evaluation cases, and a real local or remote LLM for answer generation.
- Interview positioning: "I used Ollama to run a local embedding model for the retrieval layer, then kept a sparse fallback so the demo and tests still run without model setup."

## 2026-07-28: Add Local Grounded Answer Generation

- User wanted a second small local AI model so the project could generate answers instead of only extracting source sentences.
- Decision: test `qwen3:4b` for better Chinese answer quality, then use `qwen2.5:3b` as the default generation model because the current Ollama version exposes Qwen3 reasoning text instead of a stable final answer. Keep the same grounded generation flow: only call the model after retrieval passes the relevance threshold and pass the question plus numbered source chunks to Ollama `/api/chat`.
- Failure handling: unrelated queries are rejected before generation, and an unavailable generation model falls back to extractive source-based answers.
- Performance improvement: sample documents are now indexed in one batch instead of rebuilding vectors after every file; the 27-document sample corpus indexed in about 6 seconds in the local smoke test.
- Validation: the project now uses `qwen2.5:3b` for direct Chinese answer generation, with an extractive fallback and reasoning cleanup tests; `qwen3:4b` remains installed for later Ollama upgrades. The unrelated Mars-treaty query remains refused.
- Interview positioning: "I separated retrieval and generation into two small Ollama models, constrained generation to retrieved evidence, and added refusal and fallback paths."

## 2026-07-29: Add Model Selection To The Workbench

- User wanted to compare local answer models directly from the LearningHub page.
- Decision: add `GET /api/v1/models` to discover installed Ollama generation models, add `chat_model` to the query request, and keep the selection scoped to one request instead of mutating the service default.
- Safety boundary: models without generation capability, such as `embeddinggemma:300m`, are excluded from the picker; an uninstalled requested model returns HTTP 400; low-relevance questions are still refused before generation.
- UI: add a Chinese "回答模型" selector, show the selected model in the answer status, and add a static asset version marker so browsers do not keep the old JavaScript after an update.
- Validation: the local page displayed `qwen2.5:3b`, `qwen3:4b`, and `qwen3:0.6b`; selecting another model changed the request value; the selected `qwen2.5:3b` path returned `answer_model=qwen2.5:3b`; API tests increased to 7.
