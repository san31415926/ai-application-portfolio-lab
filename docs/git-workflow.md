# Git Workflow

## First Setup

检查 Git 身份：

```powershell
git config --global user.name
git config --global user.email
```

如果没有配置：

```powershell
git config --global user.name "你的 GitHub 用户名"
git config --global user.email "你的 GitHub 邮箱"
```

## Daily Workflow

每次开始学习前：

```powershell
git pull
```

完成一个小任务后：

```powershell
git status
git add .
git commit -m "docs: update learning notes"
git push
```

## Recommended Commit Style

- `docs:` 学习笔记、README、说明文档
- `feat:` 新功能
- `fix:` 修复问题
- `refactor:` 重构
- `test:` 测试
- `chore:` 环境、依赖、配置

## Never Commit

- `.env`
- API key
- 本地上传的私人文件
- 大体积临时文件

