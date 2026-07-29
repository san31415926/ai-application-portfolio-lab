# 项目 01 学习笔记

## 任务 01：读取 PDF

日期：2026-07-22

### 完成内容

创建了：

```text
projects/01-chat-with-pdf/read_pdf.py
```

脚本完成了以下工作：

1. 定位示例 PDF。
2. 使用 `pypdf.PdfReader` 读取 PDF。
3. 提取每一页的文本。
4. 打印基础元数据和前 500 个字符。

### 测试命令

```powershell
.venv\Scripts\python.exe projects\01-chat-with-pdf\read_pdf.py
```

### 运行结果

脚本成功读取：

- 页数：2
- 字符数：1039

提取文本包含以下内容：

```text
岗位说明、公司背景，以及 FlowAI 为销售、运营和客户支持团队构建内部 AI 工具的介绍。
```

### 关键认识

RAG 从文档解析开始。

如果系统不能可靠地从文件中提取文本，后续的文本切分、Embedding、向量检索和回答生成都会建立在不可靠的输入上。

### 下一步

任务 02 将把提取出的文本切分成更小的片段。

## 任务 02：本地 JD 知识库 MVP

日期：2026-07-27

### 完成内容

创建了：

```text
projects/01-chat-with-pdf/jd_knowledge_base.py
projects/01-chat-with-pdf/app.py
projects/01-chat-with-pdf/test_jd_knowledge_base.py
```

这个 MVP 完成了以下工作：

1. 加载 Markdown 和 PDF 来源文档。
2. 将文本切分成带重叠部分的片段。
3. 构建轻量级 TF-IDF 检索索引。
4. 将常见中文求职问题扩展为岗位、JD 和 RAG 关键词。
5. 使用来源片段组织回答。
6. 证据不足时拒答低置信度问题。

### 测试命令

```powershell
cd projects\01-chat-with-pdf
python test_jd_knowledge_base.py
```

```powershell
python projects\01-chat-with-pdf\jd_knowledge_base.py "这个岗位要求哪些技能？" --show-index
```

### 运行结果

- 单元测试：3 项通过。
- 默认加载文档：4 份。
- 建立索引的文本片段：12 个。
- 相关的 JD 技能问题可以返回 JD 和项目 README 中的来源片段。
- 无关问题会返回拒答信息。

### 关键认识

一个适合写进简历的 AI 项目需要有可见行为和失败处理。即使还没有加入 Embedding 或 LLM，这个 MVP 也展示了 RAG 的核心循环：加载文档、切分文本、检索上下文、基于来源回答，以及证据不足时拒答。

### 下一步

任务 03 将用 Embedding 检索替换词法检索，并把向量存入 Chroma 或 FAISS。

## 任务 03：模拟职业数据库

日期：2026-07-27

### 完成内容

创建了：

```text
projects/01-chat-with-pdf/career_database.py
projects/01-chat-with-pdf/test_career_database.py
data/processed/ai_career_demo.sqlite
```

模拟 SQLite 数据库包含：

- 5 个 AI 职业岗位
- 16 项技能
- 岗位与技能的要求关系
- 作品集项目推荐
- 技能与项目证据的关联
- 面试问题
- 学习任务

### 测试命令

```powershell
cd projects\01-chat-with-pdf
python test_career_database.py
```

```powershell
python projects\01-chat-with-pdf\career_database.py --init --query projects --role-id 1
```

### 运行结果

- 数据库测试：5 项通过。
- 项目测试合计：8 项通过。
- 当前项目在模拟的“初级 AI 应用工程师”岗位中排名第一，匹配 8 项岗位要求技能。

### 关键认识

这个项目已经不只是文本检索演示，还具备一个规模虽小但容易解释的业务数据模型，把岗位、技能、作品集证据、学习任务和面试准备连接起来。
