# Task 01: Read A PDF

## Goal

先不要急着做完整 RAG。

这一步只做一件事：

> 用 Python 读取一个 PDF，并打印前 500 个字符。

## Material

练习 PDF：

```text
samples/pdf/ai_application_engineer_jd.pdf
```

## Why This Task Matters

RAG 的第一步不是大模型，也不是向量数据库，而是拿到干净的文本。

如果 PDF 文本读取失败，后面的 chunk、embedding、retriever 都没有意义。

## Your Steps

### 1. Create A Virtual Environment

```powershell
python -m venv .venv
```

### 2. Activate It

```powershell
.venv\Scripts\Activate.ps1
```

如果 PowerShell 拦截脚本执行，先运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

然后再激活虚拟环境。

### 3. Install Only What You Need

这一步先不要安装全部依赖，只安装读取 PDF 需要的包：

```powershell
pip install pypdf python-dotenv
```

### 4. Create A Small Script

在这个目录下创建：

```text
projects/01-chat-with-pdf/read_pdf.py
```

你先尝试自己写。

提示：

```python
from pathlib import Path
from pypdf import PdfReader

pdf_path = Path("samples/pdf/ai_application_engineer_jd.pdf")
reader = PdfReader(pdf_path)

text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

print(text[:500])
```

## Checkpoint

如果你看到类似下面的信息，就说明成功了：

```text
AI Application Engineer Job Description
Company Background
FlowAI is a small software company...
```

## Reflection Questions

完成后，你要能回答：

1. PDF 读取出来的结果是完整的吗？
2. 换一个 PDF 会不会读取失败？
3. 为什么 RAG 项目的第一步是文档解析？

