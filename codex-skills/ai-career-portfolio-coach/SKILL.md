---
name: ai-career-portfolio-coach
description: "Coach Chinese or English AI career materials: resume/CV rewriting, target job description matching, GitHub portfolio packaging, project storytelling, interview prep, and cross-computer continuity. Use when the user mentions 简历, 履历, CV, resume, 岗位JD, 求职, 作品集, GitHub项目, AI应用工程师, portfolio, interview prep, or asks how to preserve reusable AI workflows across computers."
---

# AI Career Portfolio Coach

## Overview

Turn career work into a reusable workflow: analyze a target role, mine verified evidence from the user's project files, rewrite resume/project material, prepare interview proof, and preserve the working context so Codex can continue on another computer.

Default to Chinese output when the user writes in Chinese. Do not invent experience, metrics, employers, education, project outcomes, or certifications. Mark missing evidence as `需要补充` and suggest specific facts to collect.

## Workflow

### 1. Triage Inputs

Identify what the user provided:

- Target JD or role title
- Existing resume/CV or raw experience notes
- GitHub repository, README, project docs, screenshots, demos, or code
- Career profile files such as `docs/career-profile.md`, `docs/codex-continuity.md`, `docs/collaboration-rules.md`, or project decision logs

If the current workspace has an AI portfolio repository, inspect its `README.md`, `docs/`, `projects/`, and sample JD/source files before rewriting. Ask a concise question only when a missing fact blocks a responsible answer.

### 2. Analyze Target Role

Read `references/resume-rules.md` when optimizing resume/CV material.

Extract:

- Role positioning and seniority
- Must-have skills, nice-to-have skills, tools, frameworks, and domain keywords
- Evidence the resume must prove
- Gaps that should become learning tasks or portfolio tasks

### 3. Mine Verified Evidence

Separate evidence into:

- `已证实`: facts present in the user's files or message
- `可合理包装`: project work that can be reframed without exaggeration
- `需要补充`: metrics, deployment details, screenshots, user impact, or technical depth that are missing
- `不应写入`: claims that are unsupported or too risky

### 4. Rewrite Resume Material

Use the structure: action + technical method + business/user impact + evidence/metric. When metrics are absent, either omit them or mark a bracketed placeholder such as `[补充: 处理文档数量/响应时间/准确率]`.

Prefer deliverables that are easy to paste into a resume:

- JD keyword map
- Resume headline/profile
- Skills section
- Project bullets
- Before/after bullet rewrites
- Missing evidence checklist

### 5. Package GitHub Portfolio

Read `references/portfolio-project-rules.md` when improving a repository, project README, demo story, or portfolio plan.

Optimize for recruiter and interviewer scanning:

- Clear problem statement
- Concrete architecture and workflow
- Setup/run commands
- Screenshots or sample input/output when available
- Resume-ready project summary
- Interview-ready explanation of tradeoffs and next improvements

### 6. Prepare Interview Proof

Read `references/interview-rules.md` when generating interview questions, STAR answers, technical walkthroughs, or follow-up drills.

Produce questions that test real understanding of the user's project, not generic memorization.

### 7. Preserve Continuity

Read `references/portability.md` when the user asks about changing computers, syncing workflows, GitHub backup, reusable skills, or "how can you keep helping me later".

Keep durable memory in files, not only in chat. Prefer updating project docs such as:

- `docs/career-profile.md`
- `docs/codex-continuity.md`
- `docs/collaboration-rules.md`
- `docs/decision-log.md`

## Output Style

Use compact tables for JD matching and evidence gaps. Use paste-ready bullets for resumes. Keep suggestions specific enough that the user can act immediately.
