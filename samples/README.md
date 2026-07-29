# 示例素材

这些是练习“项目 01：PDF 对话”时使用的模拟素材。

素材不是最终项目成果，只是为了让你在没有真实 PDF 的时候，也能马上练习：

- PDF 读取
- 文本切分
- 向量检索
- 基于来源回答

## 素材文件

- `source/ai_application_engineer_jd.md`: 模拟 AI 应用工程师岗位 JD。
- `source/rag_learning_notes.md`: 模拟 RAG 学习笔记。
- `pdf/ai_application_engineer_jd.pdf`: 由脚本根据中文岗位说明生成的练习 PDF。

## 重新生成 PDF

```powershell
python scripts/make_sample_pdf.py
```

生成脚本使用 `reportlab` 的中文 CID 字体，生成后的 PDF 仍可由 `pypdf` 提取中文文本。

