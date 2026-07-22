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

