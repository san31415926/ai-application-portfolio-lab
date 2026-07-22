# Troubleshooting Rules

这个文件记录我们学习项目时的排错约定。

以后如果换电脑、换环境、换依赖版本，先看这里。

## Core Rule

遇到项目跑不通，不要急着大改代码。

优先按这个顺序排查：

1. 先读完整报错信息。
2. 判断问题类型：路径、依赖、Python 版本、API key、网络、模型接口、库版本变化。
3. 查当前仓库已有代码和文档。
4. 查官方文档。
5. 查 GitHub 上的相关资料：
   - 官方仓库 README
   - Issues
   - Discussions
   - Pull requests
   - Release notes
6. 找到解决办法后，只改最小必要代码。
7. 运行验证命令。
8. 把问题、原因、解决方法记录到学习笔记。

## Why GitHub First

LangChain、Chroma、OpenAI SDK、Streamlit 这类库更新很快。

很多报错不是你写错了，而是：

- 教程过期了。
- 包版本变了。
- API 名称改了。
- 示例代码不兼容新版依赖。

所以遇到奇怪问题时，要优先确认 GitHub issue 或官方文档里有没有现成解释。

## How To Ask Codex For Help

把这些信息发给 Codex：

```text
我运行了什么命令：

完整报错：

我改过哪些文件：

我现在想达到什么效果：
```

Codex 应先查本地项目，再查官方文档或 GitHub 相关 issue，然后解释原因并带我一步步修。

