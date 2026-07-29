# 任务 01：读取 PDF

## 目标

先不要急着做完整 RAG。

这一步只做一件事：

> 用 Python 读取一个 PDF，并打印前 500 个字符。

## 练习素材

练习 PDF：

```text
samples/pdf/ai_application_engineer_jd.pdf
```

## 为什么要做这一步

RAG 的第一步不是大模型，也不是向量数据库，而是拿到干净的文本。

如果 PDF 文本读取失败，后面的 chunk、embedding、retriever 都没有意义。

## 操作步骤

### 1. 创建虚拟环境

```powershell
python -m venv .venv
```

### 2. 激活虚拟环境

```powershell
.venv\Scripts\Activate.ps1
```

如果 PowerShell 拦截脚本执行，先运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

然后再激活虚拟环境。

### 3. 只安装当前需要的依赖

这一步先不要安装全部依赖，只安装读取 PDF 需要的包：

```powershell
pip install pypdf python-dotenv
```

### 4. 创建一个小脚本

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

## 检查点

如果你看到包含“岗位说明”“公司背景”和“FlowAI”等内容，就说明成功了：

```text
AI 应用工程师岗位说明
公司背景
FlowAI 是一家为销售、运营和客户支持团队构建内部 AI 工具的小型软件公司……
```

## 复盘问题

完成后，你要能回答：

1. PDF 读取出来的结果是完整的吗？
2. 换一个 PDF 会不会读取失败？
3. 为什么 RAG 项目的第一步是文档解析？

