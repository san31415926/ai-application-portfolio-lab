# Career Profile

Use this file as durable context for Codex. Keep facts specific and update it whenever resume direction changes.

## Target Roles

- Primary target: Junior AI Application Engineer
- Secondary targets: AI application developer, LLM application engineer, RAG prototype developer
- Preferred industries: AI tools, internal productivity tools, sales/operations/customer-support tooling
- Preferred city/remote:

## Current Positioning

- Current background: Building a resume-ready AI application engineering portfolio.
- Strongest technical evidence: `projects/02-rag-fastapi-service` now implements LearningHub with upload, chunking, Ollama local embedding retrieval (`embeddinggemma:300m`), selectable grounded local answer generation, source citations, refusal and fallback behavior, note CRUD, related source retrieval, a Chinese workbench, sample corpus loading, model discovery, and tests.
- Strongest project evidence: The flagship project is now modeled after `RMA-MUN/RAGNotebook`, but simplified into a defensible portfolio prototype instead of copying the full MySQL/Redis/React/Tiptap stack.
- Biggest gap to close: Persist vectors with Chroma, persist notes in SQLite/MySQL, add screenshots, extend local LLM generation to writing assistance, and document evaluation cases.

## Skills To Highlight

- Programming: Python, file parsing, command-line workflow
- AI/LLM: RAG pipeline, chunking, Ollama local embedding retrieval, grounded Qwen generation, source citation, low-confidence refusal, generation fallback, note-related retrieval
- Data: Markdown/TXT/PDF ingestion, custom LearningHub tutorial corpus with 27 Markdown learning documents
- Web/backend: FastAPI, REST API design, OpenAPI docs, static Chinese notebook workbench, router/service layering
- Tools: Git, `.env.example`, requirements management, troubleshooting docs

## Portfolio Projects

| Project | Status | Resume value | Missing evidence |
| --- | --- | --- | --- |
| LearningHub | MVP runnable | Shows FastAPI backend design, Chinese notebook workbench, document upload, chunking, two Ollama local models, grounded generation, source citations, refusal behavior, fallback, note CRUD, sample tutorial corpus, API docs, and unit tests | Chroma upgrade, persistent DB, screenshots, evaluation notes, deployment URL |
| Chat with PDF / AI JD Knowledge Base | Earlier prototype | Shows PDF/Markdown ingestion, chunking, local retrieval, SQLite demo querying, source snippets, and low-confidence refusal | De-emphasize in resume unless needed as background |

## Resume Source Facts

Add only facts that are true and defensible in interviews.

- Education:
- Work experience:
- Certifications:
- Measured achievements: `projects/02-rag-fastapi-service` uses Ollama `embeddinggemma:300m` for 768-dimensional retrieval vectors and a selectable local chat model for grounded Chinese answers, with sparse retrieval and extractive-answer fallbacks. It includes 27 tutorial Markdown documents, 5 sample notes, source citations, low-confidence refusal, batch indexing, note workflows, model discovery, OpenAPI docs, and 7 passing API tests. A local smoke test indexed the 27-document corpus in about 6 seconds, answered a C-language question with `qwen2.5:3b`, and correctly refused an unrelated Mars-treaty query. Earlier prototype: sample JD PDF read successfully, local JD knowledge base indexes default documents, SQLite demo database contains 5 roles and 16 skills, 8 unit tests pass.
- Links:

## Writing Preferences

- Default language: Chinese
- Resume style: concise, evidence-heavy, no exaggerated claims
- Interview prep style: ask practical follow-up questions based on my actual projects
