# Codex Continuity

This project is designed so Codex can continue helping from another computer.

## Restore On Another Computer

1. Clone or copy this repository.
2. Copy the bundled skill backup from this repository:

```text
codex-skills/ai-career-portfolio-coach/
```

into the new computer's personal Codex skills folder:

```text
~/.codex/skills/ai-career-portfolio-coach/
```

On Windows:

```text
C:\Users\<you>\.codex\skills\ai-career-portfolio-coach\
```

3. Create `.env` from `.env.example` and fill local API keys.
4. Install project dependencies.
5. Start a new Codex task in this repository and say:

```text
Use $ai-career-portfolio-coach. Read docs/career-profile.md and docs/codex-continuity.md first, then continue helping me with this resume project.
```

## What Codex Should Read First

- `docs/career-profile.md`
- `docs/collaboration-rules.md`
- `docs/decision-log.md`
- `docs/git-workflow.md`
- `docs/learning-roadmap.md`
- `projects/02-rag-fastapi-service/README.md`
- root `README.md`

Current flagship project:

```text
projects/02-rag-fastapi-service/  # LearningHub
```

## What To Keep Updated

- Target roles and JD links
- Real resume facts
- Project status
- Screenshots or sample outputs
- Decisions that affect resume positioning

## Do Not Commit

- `.env`
- API keys
- private resumes with sensitive contact information, unless this repository is intentionally private
- raw personal documents that should not be shared
