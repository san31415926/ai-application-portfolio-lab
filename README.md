# AI 应用作品集实验室

这是一个面向 AI 应用工程师岗位的作品集项目仓库。

目标不是展示提示词、学习笔记或课程截图，而是把课程项目和开源案例拆开理解后，改造成可以运行、可以测试、可以讲清楚技术取舍的简历项目。

## 当前旗舰项目

**LearningHub**

这是一个参考 `RMA-MUN/RAGNotebook` 产品方向做的轻量版中文 RAG Notebook。项目重点不是学习笔记或提示词整理，而是一个可运行、可测试、带中文工作台、可通过 OpenAPI 查看接口的 AI 知识管理项目。项目背景、处理链路、简历表述和面试讲法统一记录在 [`docs/learninghub-project-summary.md`](docs/learninghub-project-summary.md)。

当前版本保留了简历项目最有价值的后端能力：

```text
FastAPI 路由 -> 文档上传 -> 文本切分 -> embeddinggemma 向量 -> 检索 -> 可选择的本地聊天模型 -> 来源约束回答 -> 笔记 -> 相关来源
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

## 技术重点

- RAG 文档问答
- 本地 embedding 检索与可选择的本地生成模型
- Agent 工具调用
- 数据分析助手
- Web 信息抽取
- 多步骤研究报告生成
- AI 应用工程化：配置、日志、README、部署、演示

## 项目路线图

| 阶段 | 项目 | 状态 | 简历价值 |
| --- | --- | --- | --- |
| 1 | PDF 对话 / 基础 RAG | 已完成早期原型 | 理解 PDF 读取和基础检索 |
| 2 | LearningHub | MVP 可运行 | 展示 FastAPI、双本地模型、向量检索、来源约束生成、拒答和笔记管理 |
| 3 | Chroma 向量库升级 | 下一步 | 从内存向量检索升级为可持久化 Notebook RAG |
| 4 | 数据分析 Agent | 待开始 | 面向业务数据的 AI 助手 |

## 仓库结构

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

## 运行 FastAPI 服务

在仓库根目录执行，首次使用时安装依赖，然后启动 API 服务：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

ollama pull embeddinggemma:300m
ollama pull qwen2.5:3b
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir projects\02-rag-fastapi-service --host 127.0.0.1 --port 8010
```

Windows 通常会在后台启动 Ollama。如果 `ollama list` 无法连接，请先在另一个终端运行 `ollama serve`。只有需要修改默认模型或后端时，才需要将 `.env.example` 复制为 `.env`。

打开页面和 API 文档：

```text
http://localhost:8010/app/
http://localhost:8010/docs
```

加载示例资料：

```powershell
Invoke-RestMethod -Method Post http://localhost:8010/api/v1/knowledge/documents/samples
Invoke-RestMethod -Method Post http://localhost:8010/api/v1/notes/samples

Invoke-RestMethod -Method Post http://localhost:8010/api/v1/chat/query `
  -ContentType "application/json" `
  -Body '{"query":"C 语言中的变量怎么理解？","top_k":3,"chat_model":"qwen2.5:3b"}'
```

运行测试：

```powershell
cd projects\02-rag-fastapi-service
python -m unittest discover -s tests
```

## 简历表述

- 参考 RAGNotebook 产品形态，基于 FastAPI 实现 LearningHub 中文学习知识库，接入 Ollama 本地 `embeddinggemma:300m` 和 `qwen2.5:3b`，完成语义检索、来源约束回答和低相关度拒答。
- 增加本地模型发现与按请求选择机制，页面可在 `qwen2.5:3b`、`qwen3:4b` 等已安装生成模型之间切换，embedding 模型不参与回答模型选择。
- 设计 RAG + Notebook 服务分层结构，将路由层、文档解析、文本切分、检索器、问答服务、笔记服务和静态中文工作台解耦，并通过 OpenAPI 文档暴露可测试接口。
- 自建 LearningHub 学习教程库样例，包含 27 份 Markdown 教程文档，覆盖做菜、C 语言入门、Python、Excel、SQL、Git、英语、数学、Pandas、RAG 等主题，用于演示中文教程检索、学习笔记和来源追踪。
- 实现低置信度拒答、生成失败降级、批量向量索引和笔记关联知识库机制，通过测试覆盖示例入库、文档上传、查询命中、无证据拒答和笔记关联场景。

## 换电脑继续使用

1. 克隆这个仓库。
2. 创建 Python 虚拟环境。
3. 将 `.env.example` 复制为 `.env`。
4. 安装 Ollama，并拉取项目需要的本地模型。
5. 按照 `projects/` 中的任务卡继续学习。
6. 如果希望 Codex 保持相同的工作方式，将 `codex-skills/ai-career-portfolio-coach/` 复制到 `~/.codex/skills/`。

不要提交 `.env` 或私有 API 密钥。

## 排错约定

项目无法运行时，先查看 `docs/troubleshooting-rules.md`。

排错原则是：先读完整报错，判断可能原因；依赖发生变化时查阅官方文档和 GitHub issue；找到原因后只做最小且经过验证的修复。

## 协作说明

长期项目偏好记录在 `docs/collaboration-rules.md` 中。
