# Codex 持续协作说明

这个项目通过仓库文件保存上下文，换电脑后 Codex 也可以继续协作。

## 在另一台电脑恢复

1. 克隆或复制这个仓库。
2. 复制仓库内备份的技能文件夹：

```text
codex-skills/ai-career-portfolio-coach/
```

将它放入新电脑的 Codex 个人技能目录：

```text
~/.codex/skills/ai-career-portfolio-coach/
```

Windows 路径通常是：

```text
C:\Users\<用户名>\.codex\skills\ai-career-portfolio-coach\
```

3. 根据 `.env.example` 创建 `.env`，填写本机需要的配置。
4. 安装项目依赖。
5. 在这个仓库中新建 Codex 任务，并发送：

```text
使用 $ai-career-portfolio-coach。先阅读 docs/career-profile.md 和 docs/codex-continuity.md，然后继续帮助我完成这个简历项目。
```

## Codex 首先应阅读的文件

- `docs/career-profile.md`
- `docs/collaboration-rules.md`
- `docs/decision-log.md`
- `docs/git-workflow.md`
- `docs/learning-roadmap.md`
- `projects/02-rag-fastapi-service/README.md`
- `docs/datapilot-project-plan.md`
- `projects/03-data-analysis-agent/README.md`
- 根目录 `README.md`

当前旗舰项目：

```text
projects/02-rag-fastapi-service/  # LearningHub
```

当前规划中的第二个简历项目：

```text
projects/03-data-analysis-agent/  # DataPilot：本地自然语言数据分析 Agent
```

DataPilot 的完整执行计划保存在：

```text
docs/datapilot-project-plan.md
```

计划状态：已完成上游项目分析、选题和边界冻结；阶段 2 项目骨架、独立依赖和最小 Streamlit 启动页已完成；阶段 3 中文电商 CSV/XLSX 样例数据已生成并通过测试；阶段 4 文件读取、编码处理、字段清洗和类型识别已完成；阶段 5 数据概览和质量检查已完成；阶段 6 DuckDB 只读查询、安全校验和中文工作台已完成，完整测试达到 30 项。下一步是阶段 7 Pydantic 工具契约与受控工具。后续必须按计划逐阶段开发、测试和更新记录，不把未验证的功能写入简历。

## 需要持续更新的内容

- 目标岗位和 JD 链接
- 真实简历事实
- 项目状态
- 截图或示例输出
- 影响简历定位的技术决策

## 不要提交的内容

- `.env`
- API 密钥
- 包含敏感联系方式的私人简历，除非仓库明确设置为私有并专门用于保存它
- 不应共享的原始个人文档
