# AI Application Portfolio Lab

这是一个面向 AI 应用工程师岗位的学习型简历项目仓库。

目标不是一次性复制开源案例，而是从 `awesome-llm-apps` 中挑选合适案例，逐步理解、复现、改造，并沉淀成可以讲清楚的作品。

## Learning Focus

- RAG 文档问答
- Agent 工具调用
- 数据分析助手
- Web 信息抽取
- 多步骤研究报告生成
- AI 应用工程化：配置、日志、README、部署、演示

## Project Roadmap

| 阶段 | 项目 | 状态 | 简历价值 |
| --- | --- | --- | --- |
| 1 | Chat with PDF / Basic RAG | 准备中 | 理解 RAG 全流程 |
| 2 | 数据分析 Agent | 待开始 | 面向业务数据的 AI 助手 |
| 3 | Web Research Agent | 待开始 | 工具调用和自动报告 |
| 4 | Agentic RAG 优化 | 待开始 | 查询改写、拒答、纠错 |

## Repository Structure

```text
.
├── docs/
│   ├── git-workflow.md
│   ├── learning-roadmap.md
│   └── project-ideas.md
├── projects/
│   └── 01-chat-with-pdf/
├── .env.example
├── .gitignore
└── README.md
```

## How To Continue On Another Computer

1. Clone this repository.
2. Create a virtual environment.
3. Copy `.env.example` to `.env`.
4. Fill in your API keys locally.
5. Follow the task cards in `projects/`.

Do not commit `.env` or private API keys.

## Troubleshooting Agreement

When something does not run, check `docs/troubleshooting-rules.md` first.

The rule is: read the error, identify the likely cause, check official docs and GitHub issues when dependencies may have changed, then make the smallest verified fix.
