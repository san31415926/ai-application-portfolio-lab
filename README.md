# AI Application Portfolio Lab

这是一个面向 AI 应用工程师岗位的作品集项目仓库。

目标不是展示提示词、学习笔记或课程截图，而是把课程项目和开源案例拆开理解后，改造成可以运行、可以测试、可以讲清楚技术取舍的简历项目。

## Current Flagship Project

**LearningHub**

这是一个参考 `RMA-MUN/RAGNotebook` 产品方向做的轻量版中文 RAG Notebook。项目重点不是学习笔记或提示词整理，而是一个可运行、可测试、带中文工作台、可通过 OpenAPI 查看接口的 AI 知识管理项目。项目背景、处理链路、简历表述和面试讲法统一记录在 [`docs/learninghub-project-summary.md`](docs/learninghub-project-summary.md)。

当前版本保留了简历项目最有价值的后端能力：

```text
FastAPI routers -> document upload -> text chunks -> embeddinggemma vectors -> retrieval -> selectable local chat model -> grounded answer -> notes -> related sources
```

核心项目目录：

```text
projects/02-rag-fastapi-service/
```

服务提供：

- `POST /api/v1/knowledge/documents/upload`：上传 `.txt`、`.md`、`.pdf`
- `POST /api/v1/knowledge/documents/samples`：加载示例教程文档
- `GET /api/v1/knowledge/stats`：查看知识库统计
- `GET /api/v1/knowledge/documents`：查看知识库文档
- `GET /api/v1/knowledge/documents/{document_id}/chunks`：查看切片
- `POST /api/v1/chat/query`：执行 RAG 问答并返回来源片段
- `GET /api/v1/models`：发现本机已安装的 Ollama 生成模型
- `POST /api/v1/notes`：创建笔记
- `GET /api/v1/notes`：查看笔记列表
- `GET /api/v1/notes/{note_id}/related`：按笔记内容检索相关来源
- `POST /api/v1/notes/{note_id}/assist`：生成摘要、续写、待办或标签建议
- `GET /api/v1/reviews/due`：查看待回顾笔记
- `GET /app/`：中文 RAG Notebook 工作台
- `GET /docs`：FastAPI 自动生成的接口文档

## Engineering Focus

- RAG 文档问答
- 本地 embedding 检索与可选择的本地生成模型
- Agent 工具调用
- 数据分析助手
- Web 信息抽取
- 多步骤研究报告生成
- AI 应用工程化：配置、日志、README、部署、演示

## Project Roadmap

| 阶段 | 项目 | 状态 | 简历价值 |
| --- | --- | --- | --- |
| 1 | Chat with PDF / Basic RAG | 已完成早期原型 | 理解 PDF 读取和基础检索 |
| 2 | LearningHub | MVP 可运行 | 展示 FastAPI、双本地模型、向量检索、来源约束生成、拒答和笔记管理 |
| 3 | Chroma 向量库升级 | 下一步 | 从内存向量检索升级为可持久化 Notebook RAG |
| 4 | 数据分析 Agent | 待开始 | 面向业务数据的 AI 助手 |

## Repository Structure

```text
.
├── docs/
│   ├── git-workflow.md
│   ├── learning-roadmap.md
│   ├── project-ideas.md
│   ├── career-profile.md
│   ├── codex-continuity.md
│   └── skill-demo-output.md
├── projects/
│   ├── 01-chat-with-pdf/
│   └── 02-rag-fastapi-service/
│       ├── app/
│       │   ├── routers/
│       │   ├── services/
│       │   ├── core/
│       │   ├── schemas.py
│       │   └── main.py
│       ├── samples/
│       ├── tests/
│       └── README.md
├── codex-skills/
│   └── ai-career-portfolio-coach/
├── .env.example
├── .gitignore
└── README.md
```

## Run The FastAPI Service

From repository root, install dependencies once and start the API server:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

ollama pull embeddinggemma:300m
ollama pull qwen2.5:3b
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir projects\02-rag-fastapi-service --host 127.0.0.1 --port 8010
```

Windows normally starts Ollama in the background. If `ollama list` cannot connect, run `ollama serve` in a separate terminal first. Copy `.env.example` to `.env` only when you need to change the default model or backend.

Open API docs:

```text
http://localhost:8010/app/
http://localhost:8010/docs
```

Load sample documents:

```powershell
Invoke-RestMethod -Method Post http://localhost:8010/api/v1/knowledge/documents/samples
Invoke-RestMethod -Method Post http://localhost:8010/api/v1/notes/samples

Invoke-RestMethod -Method Post http://localhost:8010/api/v1/chat/query `
  -ContentType "application/json" `
  -Body '{"query":"C 语言中的变量怎么理解？","top_k":3,"chat_model":"qwen2.5:3b"}'
```

Run tests:

```powershell
cd projects\02-rag-fastapi-service
python -m unittest discover -s tests
```

## Resume Bullets

- 参考 RAGNotebook 产品形态，基于 FastAPI 实现 LearningHub 中文学习知识库，接入 Ollama 本地 `embeddinggemma:300m` 和 `qwen2.5:3b`，完成语义检索、来源约束回答和低相关度拒答。
- 增加本地模型发现与按请求选择机制，页面可在 `qwen2.5:3b`、`qwen3:4b` 等已安装生成模型之间切换，embedding 模型不参与回答模型选择。
- 设计 RAG + Notebook 服务分层结构，将路由层、文档解析、文本切分、检索器、问答服务、笔记服务和静态中文工作台解耦，并通过 OpenAPI 文档暴露可测试接口。
- 自建 LearningHub 学习教程库样例，包含 27 份 Markdown 教程文档，覆盖做菜、C 语言入门、Python、Excel、SQL、Git、英语、数学、Pandas、RAG 等主题，用于演示中文教程检索、学习笔记和来源追踪。
- 实现低置信度拒答、生成失败降级、批量向量索引和笔记关联知识库机制，通过测试覆盖示例入库、文档上传、查询命中、无证据拒答和笔记关联场景。

## How To Continue On Another Computer

1. Clone this repository.
2. Create a virtual environment.
3. Copy `.env.example` to `.env`.
4. Install Ollama and pull the local models required by the project.
5. Follow the task cards in `projects/`.
6. If you want Codex to keep the same workflow, copy `codex-skills/ai-career-portfolio-coach/` into `~/.codex/skills/`.

Do not commit `.env` or private API keys.

## Troubleshooting Agreement

When something does not run, check `docs/troubleshooting-rules.md` first.

The rule is: read the error, identify the likely cause, check official docs and GitHub issues when dependencies may have changed, then make the smallest verified fix.

## Collaboration Notes

Long-term project preferences are recorded in `docs/collaboration-rules.md`.
