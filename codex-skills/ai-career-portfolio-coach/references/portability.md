# 可迁移性

## 目标

让 Codex 的持续协作依赖可以复制、同步和提交的文件，而不是依赖一台电脑上的聊天记录。

## 换电脑需要迁移什么

迁移或同步两层内容：

1. 项目层：包含代码、文档、简历、JD、笔记和 `.env.example` 的仓库或文件夹。
2. 技能层：新电脑个人 Codex 技能目录下的技能文件夹。

本技能需要保留的文件夹是：

```text
~/.codex/skills/ai-career-portfolio-coach/
```

Windows 通常是：

```text
C:\Users\<用户名>\.codex\skills\ai-career-portfolio-coach\
```

## 推荐方式

项目可以使用 GitHub 或私有仓库保存。技能可以采用以下方式之一：

- 在项目仓库中保存可迁移副本，例如 `codex-skills/ai-career-portfolio-coach/`，换电脑后复制到 `~/.codex/skills/`。
- 将技能文件夹放在私有 GitHub 仓库中，再克隆或复制到 `~/.codex/skills/`。
- 将技能文件夹放在云同步目录中，换电脑后复制到 `~/.codex/skills/`。
- 将 `~/.codex/skills/ai-career-portfolio-coach/` 导出为 `.zip` 备份。

不要提交秘密信息：

- `.env`
- API 密钥
- 包含电话、邮箱和地址的私人简历，除非仓库明确设置为私有并专门用于保存它

## 持久化记忆文件

职业项目应将以下文件保存在仓库中：

- `docs/career-profile.md`：用户稳定的事实、目标岗位、技能、限制、简历材料和偏好
- `docs/codex-continuity.md`：换电脑后恢复项目和技能的方法
- `docs/collaboration-rules.md`：用户希望 Codex 如何协作
- `docs/decision-log.md`：重要决策及其原因

在另一台电脑开始工作时，可以对 Codex 说：

```text
使用 $ai-career-portfolio-coach。先阅读 docs/career-profile.md 和 docs/codex-continuity.md，然后继续帮助我完成这个简历项目。
```

## 恢复清单

1. 在新电脑安装 Codex 并登录。
2. 克隆或复制项目仓库。
3. 将 `ai-career-portfolio-coach` 复制到 `~/.codex/skills/`。
4. 根据 `.env.example` 重新创建 `.env`。
5. 安装项目依赖。
6. 在 Codex 中打开项目，并让它阅读持续协作文件。

如果技能没有出现，复制完成后重启 Codex，或新建任务后再检查。
