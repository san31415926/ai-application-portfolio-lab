# LearningHub

一个可运行的中文 RAG Notebook 简历项目，参考 `RMA-MUN/RAGNotebook` 的产品方向做了轻量化实现：把 **笔记管理 + RAG 知识库 + 写作辅助 + 来源引用 + 回顾提醒** 串成一个工作台。

这个项目不是提示词集合，也不是课程笔记展示页。它的目标是做成一个能写进简历、能在面试中现场讲清楚的 AI 应用项目。当前版本基于 FastAPI 接入 Ollama 本地模型：`embeddinggemma:300m` 负责语义检索，聊天模型负责根据命中的来源片段生成中文回答。打开页面后，系统会自动读取本机已安装的生成模型，用户可以在“回答模型”下拉框中选择本次问答使用的模型；embedding 模型不会出现在这个列表中。

## 功能

- FastAPI 后端服务，自动生成 `/docs` 交互式 API 文档
- 支持上传 `.txt`、`.md`、`.pdf` 文档
- 自动进行文本清洗和文本切分
- 接入 Ollama `embeddinggemma:300m` 本地 embedding 模型，按向量余弦相似度召回相关片段，并保留 sparse embedding 兜底
- 接入 Ollama `qwen2.5:3b` 本地生成模型，基于检索来源组织中文答案，模型不可用时自动退回原文提取回答
- 页面支持选择本机已安装的 Ollama 生成模型，每次问答可独立选择，不会修改服务默认配置
- 提供 `/api/v1/models` 模型发现接口，返回模型名称、参数规模和能力信息
- `/api/v1/chat/query` 返回答案、来源片段、相关度和拒答状态
- 支持查看文档列表、文档 chunks、知识库统计、删除文档、加载示例资料
- 支持发现本机已安装的 Ollama 生成模型，并在页面中选择本次问答使用的模型
- 笔记管理：新建、编辑、删除、搜索、标签和分类
- 笔记关联知识库：根据笔记内容检索相关来源片段
- 写作辅助：摘要、续写、待办、标签建议
- 回顾提醒：提供简化版间隔重复接口
- 提供 `/app/` 中文 RAG Notebook 工作台
- 使用测试覆盖健康检查、静态工作台、示例入库、上传、查询、拒答、笔记关联和写作辅助

## 演示

内置样例是一套虚构的 LearningHub 学习教程库和多条学习笔记，当前包含 27 份 Markdown 教程文档，约 7900 字，覆盖 C 语言、做菜、Python、Excel、SQL、Git、Linux、英语、数学、数据分析、RAG、演讲、摄影、健身、理财、园艺、急救等主题。加载样例后可以直接查询，也可以选择笔记查看关联来源：

```powershell
Invoke-RestMethod -Method Post http://localhost:8010/api/v1/knowledge/documents/samples
Invoke-RestMethod -Method Post http://localhost:8010/api/v1/notes/samples

# 查看页面可选择的本地生成模型
Invoke-RestMethod http://localhost:8010/api/v1/models

Invoke-RestMethod -Method Post http://localhost:8010/api/v1/chat/query `
  -ContentType "application/json" `
  -Body '{"query":"C 语言中的变量怎么理解？","top_k":3,"chat_model":"qwen2.5:3b"}'
```

返回结果会包含：

```json
{
  "answer": "变量是给数据起名字的一种方式...",
  "sources": [
    {
      "filename": "c_language_basics_zh.md",
      "chunk_index": 1,
      "score": 0.6255
    }
  ],
  "refused": false
}
```

## 项目故事

- **背景**：把文档问答做成一个适合学习和演示的中文 Notebook 工作台，用户可以上传教程资料、提问、查看来源，并把问题沉淀为笔记。
- **输入**：`.txt`、`.md`、`.pdf` 文档，内置 27 份中文学习教程，以及用户输入的问题和笔记内容。
- **处理**：文档解析与清洗后进行文本切分；优先调用 Ollama `embeddinggemma:300m` 生成向量并按余弦相似度检索；命中阈值后将来源片段交给默认或用户选择的本地聊天模型生成回答。
- **输出**：中文回答、来源文件、切片序号、相关度、回答模型和拒答状态；笔记还可以关联知识库来源。
- **难点**：上下文长度有限，不能把全部文档直接交给模型；检索相关度不足时要在生成前拒答；模型不可用时要保留可演示的降级路径。
- **改进**：当前向量和笔记保存在内存中，后续升级为 Chroma + SQLite，并增加检索评估集、回答质量评估和部署配置。

## 系统架构

```text
客户端
  -> FastAPI 路由
      -> 知识库路由：上传/列表/切片/删除
      -> 问答路由：查询
      -> 笔记路由：笔记/搜索/关联/辅助/回顾
  -> RagService
      -> 文档加载器
      -> 文本切分器
      -> Ollama/本地 Embedding 检索器
      -> 本地模型列表与可选择的回答生成器
      -> 带来源引用的回答生成器
  -> NoteService
      -> 笔记增删改查
      -> 笔记搜索
      -> 相关来源检索
      -> 确定性写作辅助
      -> 间隔复习计划
```

## 项目说明

- 当前检索层默认使用 Ollama `/api/embed` 调用 `embeddinggemma:300m`，在本机完成“文档切片 -> 生成向量 -> 相似度检索 -> 来源引用回答”的 RAG 主流程。
- 检索结果达到阈值后，系统调用默认或用户选择的聊天模型生成有来源约束的回答；未达到阈值时不会调用生成模型，而是直接拒答。
- 页面通过 `/api/v1/models` 发现已安装的 Ollama 生成模型。当前本机可选 `qwen2.5:3b`、`qwen3:4b` 和 `qwen3:0.6b`；`embeddinggemma:300m` 只用于 embedding，因此不会显示在回答模型列表中。
- 如果 Ollama 没有启动或模型不可用，系统会自动切换到 `LocalSparseEmbeddingModel` 兜底，保证项目仍可本地演示和测试。
- 如果生成模型不可用，系统会自动切换到原文提取式回答，不影响基本查询流程。
- 当前向量暂存在内存中，适合简历项目 MVP；后续升级路径是将向量持久化到 Chroma，并补充检索评估样例。

## 本地运行

在仓库根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

ollama pull embeddinggemma:300m
ollama pull qwen2.5:3b
# 其他已安装的生成模型也会自动出现在页面下拉框中，例如：
# ollama pull qwen3:4b
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir projects\02-rag-fastapi-service --host 127.0.0.1 --port 8010
```

如果 `ollama list` 无法连接，请先在另一个终端运行 `ollama serve`。页面会通过 `/api/v1/models` 自动读取本机可用的生成模型；`embeddinggemma:300m` 只用于检索，不会出现在“回答模型”下拉框中。

打开：

```text
http://localhost:8010/app/
http://localhost:8010/docs
```

## API 调用示例

加载示例资料：

```powershell
Invoke-RestMethod -Method Post http://localhost:8010/api/v1/knowledge/documents/samples
Invoke-RestMethod -Method Post http://localhost:8010/api/v1/notes/samples
```

提出问题：

```powershell
Invoke-RestMethod -Method Post http://localhost:8010/api/v1/chat/query `
  -ContentType "application/json" `
  -Body '{"query":"P0 incident acknowledgement timeline","top_k":3}'
```

选择指定的本地回答模型：

```powershell
Invoke-RestMethod -Method Post http://localhost:8010/api/v1/chat/query `
  -ContentType "application/json" `
  -Body '{"query":"C 语言中的变量怎么理解？","top_k":3,"chat_model":"qwen2.5:3b"}'
```

上传文档：

```powershell
curl.exe -X POST http://localhost:8010/api/v1/knowledge/documents/upload `
  -F "file=@projects/02-rag-fastapi-service/samples/refund_policy_zh.md"
```

查看知识库统计：

```powershell
Invoke-RestMethod http://localhost:8010/api/v1/knowledge/stats
Invoke-RestMethod http://localhost:8010/api/v1/notes/stats
```

创建笔记：

```powershell
Invoke-RestMethod -Method Post http://localhost:8010/api/v1/notes `
  -ContentType "application/json" `
  -Body '{"title":"RAG Notebook 项目定位","content":"把文档问答升级成笔记和知识库联动的工作台。","tags":["RAG","Notebook"],"category":"简历项目"}'
```

## 测试

```powershell
cd projects\02-rag-fastapi-service
python -m unittest discover -s tests
```

测试默认使用稀疏检索和提取式回答降级，因此不依赖 Ollama 也能运行。当前 API 测试共 7 项；要验证本地 Embedding 和聊天模型路径，请保持 Ollama 运行并使用上面的示例 API 调用。

## 简历表述

- 参考 RAGNotebook 产品形态，基于 FastAPI 实现 LearningHub 中文学习知识库，接入 Ollama 本地 `embeddinggemma:300m` 和 `qwen2.5:3b`，完成语义检索、来源约束回答和低相关度拒答。
- 设计本地模型发现与按请求选择机制，通过 `/api/v1/models` 暴露已安装生成模型，前端下拉选择后将 `chat_model` 传入问答接口，支持在同一知识库中对比不同模型的回答效果。
- 设计 RAG + Notebook 服务分层结构，将路由层、文档解析、文本切分、检索器、问答服务、笔记服务和静态中文工作台解耦，并通过 OpenAPI 文档暴露可测试接口。
- 自建 LearningHub 学习教程库样例，包含 27 份 Markdown 教程文档，覆盖做菜、C 语言入门、Python、Excel、SQL、Git、英语、数学、Pandas、RAG 等主题，用于演示中文教程检索、学习笔记和来源追踪。
- 实现低置信度拒答、生成失败降级、批量向量索引和笔记关联知识库机制，通过测试覆盖静态工作台、示例入库、文档上传、查询命中、无证据拒答和笔记关联场景。

## 下一步

- 将内存向量索引升级为 Chroma 向量库
- 补充检索评估样例和阈值调优记录
- 将内存笔记存储升级为 SQLite 或 MySQL
- 接入真实 LLM 做流式写作辅助
- 增加用户隔离、登录和会话历史
- 将静态页面升级为 React + Markdown 编辑器
