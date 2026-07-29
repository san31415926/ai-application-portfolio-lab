# Project 01 Notes

## Task 01: Read A PDF

Date: 2026-07-22

### What We Built

Created:

```text
projects/01-chat-with-pdf/read_pdf.py
```

The script:

1. Locates the sample PDF.
2. Reads it with `pypdf.PdfReader`.
3. Extracts text from every page.
4. Prints basic metadata and the first 500 characters.

### Test Command

```powershell
.venv\Scripts\python.exe projects\01-chat-with-pdf\read_pdf.py
```

### Result

The script successfully read:

- Pages: 2
- Characters: 2871

The extracted text starts with:

```text
AI Application Engineer Job Description
Company Background
FlowAI is a small software company building internal AI tools...
```

### Key Lesson

RAG starts with document parsing.

If the system cannot reliably extract text from a file, then chunking, embeddings, vector search, and answer generation will all be built on weak input.

### Next Step

Task 02 should split the extracted text into smaller chunks.

## Task 02: Local JD Knowledge Base MVP

Date: 2026-07-27

### What We Built

Created:

```text
projects/01-chat-with-pdf/jd_knowledge_base.py
projects/01-chat-with-pdf/app.py
projects/01-chat-with-pdf/test_jd_knowledge_base.py
```

The MVP:

1. Loads Markdown and PDF source documents.
2. Splits text into chunks with overlap.
3. Builds a lightweight TF-IDF retrieval index.
4. Expands common Chinese career questions into role/JD/RAG keywords.
5. Answers with source snippets.
6. Refuses low-confidence questions when evidence is missing.

### Test Commands

```powershell
cd projects\01-chat-with-pdf
python test_jd_knowledge_base.py
```

```powershell
python projects\01-chat-with-pdf\jd_knowledge_base.py "这个岗位要求哪些技能？" --show-index
```

### Result

- Unit tests: 3 passed.
- Indexed default documents: 4.
- Indexed chunks: 12.
- A relevant JD skill question returns source snippets from the JD and project README.
- An unrelated question returns a refusal message.

### Key Lesson

A resume-ready AI project needs visible behavior and failure handling. Even before adding embeddings or an LLM, this MVP demonstrates the core RAG loop: load documents, chunk text, retrieve context, answer with sources, and refuse when evidence is weak.

### Next Step

Task 03 should replace lexical retrieval with embeddings and store vectors in Chroma or FAISS.

## Task 03: Simulated Career Database

Date: 2026-07-27

### What We Built

Created:

```text
projects/01-chat-with-pdf/career_database.py
projects/01-chat-with-pdf/test_career_database.py
data/processed/ai_career_demo.sqlite
```

The simulated SQLite database contains:

- 5 AI career roles
- 16 skills
- role-skill requirement links
- portfolio project recommendations
- skill-project evidence links
- interview questions
- learning tasks

### Test Commands

```powershell
cd projects\01-chat-with-pdf
python test_career_database.py
```

```powershell
python projects\01-chat-with-pdf\career_database.py --init --query projects --role-id 1
```

### Result

- Database tests: 5 passed.
- Total project tests: 8 passed.
- The current project ranks first for the simulated "初级 AI 应用工程师" role, matching 8 required skills.

### Key Lesson

The project is no longer only a text retrieval demo. It now has a small but explainable business data model that connects roles, skills, portfolio evidence, learning tasks, and interview preparation.

