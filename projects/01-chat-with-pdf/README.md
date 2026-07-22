# Project 01: Chat With PDF

## Goal

从一个基础 PDF 问答案例开始，逐步改造成“AI 求职资料问答助手”。

你最终要能解释清楚：

> 用户上传 PDF 后，系统如何把文档变成可检索知识库？用户提问时，系统如何找到相关片段，再让大模型基于片段回答？

## Task Cards

### Task 1: Run A Minimal Demo

目标：先跑通一个最小 PDF 问答流程。

你需要完成：

- 创建 Python 虚拟环境。
- 安装基础依赖。
- 准备一个测试 PDF。
- 读取 PDF 文本。
- 打印前 500 个字符。

不要一开始就写完整 RAG。

### Task 2: Split Text Into Chunks

目标：理解为什么长文档不能直接塞给大模型。

你需要完成：

- 把 PDF 文本切成多个 chunk。
- 打印 chunk 数量。
- 打印第一个 chunk。
- 观察 chunk_size 和 chunk_overlap 的影响。

### Task 3: Create Embeddings

目标：理解文本如何变成向量。

你需要完成：

- 配置 API key。
- 调用 embedding 模型。
- 对几个短句生成向量。
- 比较相似句子的检索结果。

### Task 4: Build A Vector Store

目标：把 chunk 存入向量数据库。

你需要完成：

- 选择 Chroma 或 FAISS。
- 存入 PDF chunks。
- 根据问题检索 top-k 片段。
- 打印检索到的上下文。

### Task 5: Generate Answers With Sources

目标：让 LLM 只基于检索到的上下文回答。

你需要完成：

- 设计 prompt。
- 把检索上下文传给 LLM。
- 回答中显示来源片段。
- 找不到答案时拒答。

## Innovation Direction

基础版完成后，改造成：

**AI Job Description Knowledge Base**

它可以回答：

- 这个岗位要求哪些技能？
- 我现在缺哪些能力？
- 这个 JD 适合放进简历的项目亮点是什么？
- 面试官可能追问什么？

