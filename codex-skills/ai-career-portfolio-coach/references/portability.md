# Portability

## Goal

Make Codex continuity depend on files that can be copied, synced, or committed, instead of depending on one chat history on one computer.

## What Must Move To A New Computer

Move or sync these two layers:

1. Project layer: the repository or folder containing code, docs, resumes, JDs, notes, and `.env.example`.
2. Skill layer: the personal skill folder under the new computer's `~/.codex/skills/`.

For this skill, the folder to preserve is:

```text
~/.codex/skills/ai-career-portfolio-coach/
```

On Windows this is usually:

```text
C:\Users\<you>\.codex\skills\ai-career-portfolio-coach\
```

## Best Practice

Use GitHub or a private repo for the project. Use one of these for the skill:

- Store a portable copy inside the project repository, for example `codex-skills/ai-career-portfolio-coach/`, then copy it into `~/.codex/skills/` on the new computer.
- Put the skill folder in a private GitHub repo and clone/copy it into `~/.codex/skills/`.
- Store the skill folder in a cloud-synced folder, then copy it into `~/.codex/skills/`.
- Keep an exported `.zip` backup of `~/.codex/skills/ai-career-portfolio-coach/`.

Do not commit secrets:

- `.env`
- API keys
- private resumes with phone/email/address unless the repository is private and intentionally used for that purpose

## Durable Memory Files

For career projects, keep these files inside the project repository:

- `docs/career-profile.md`: stable facts about the user, target roles, skills, constraints, resume material, and preferences
- `docs/codex-continuity.md`: how to restore the project and skill on another computer
- `docs/collaboration-rules.md`: how the user wants Codex to work
- `docs/decision-log.md`: important choices and why they were made

When starting on another computer, ask Codex:

```text
Use $ai-career-portfolio-coach. Read docs/career-profile.md and docs/codex-continuity.md first, then continue helping me with this resume project.
```

## Restore Checklist

1. Install Codex on the new computer and sign in.
2. Clone or copy the project repository.
3. Copy `ai-career-portfolio-coach` into `~/.codex/skills/`.
4. Recreate `.env` from `.env.example`.
5. Install project dependencies.
6. Open the project in Codex and ask it to read the continuity files.

If the skill does not appear, restart Codex or start a new task after copying the folder.
