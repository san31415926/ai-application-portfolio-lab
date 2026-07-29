# GitHub Actions 入门

## 工作流结构
GitHub Actions 使用 YAML 描述触发条件、任务和步骤。常见触发条件是推送、Pull Request 或手动执行，任务可以安装依赖、运行测试和构建项目。

## CI 流程
一个基础 Python 流程通常包括设置 Python 版本、安装依赖、运行 `pytest` 和检查代码格式。测试失败时工作流应失败，避免错误代码进入主分支。

## 使用注意
Action 版本要固定或定期更新，敏感配置放在 Secrets。日志中不要输出 Token、密码和完整请求头，工作流权限也应遵循最小权限原则。
