# MySkill

个人 Claude Code 技能集合。每个子目录是一个可独立安装的 Skill。

## 技能

| 技能 | 说明 |
|------|------|
| `kb/` | 本地 RAG 知识库，语义检索 + 智能删除 |
| `pdf-to-markdown/` | PDF/文档转 Markdown，基于 MinerU API |
| `make-tutorial/` | 专业级中文教程生成（多文件 HTML 站点） |
| `godot-procedural-kit/` | Godot 程序化内容工具包 |
| `send-email-skill/` | SMTP 邮件发送，支持 HTML 和附件 |

## 快速开始

### 安装

将技能目录复制到 `~/.claude/skills/` 即可：

```bash
cp -r MySkill/kb ~/.claude/skills/
```

或一键分发全部（Windows）：

```bat
distribute.bat
```

### 新建技能

参考 [NEW.md](NEW.md)。

## 规范

- **[ENV.md](ENV.md)** — 敏感配置三件套：`.env.example` + `.env` + `_load_env()`
- **[NEW.md](NEW.md)** — 新建 Skill 模板与 Checklist

## 要求

- Python 3.x（部分 Skill 脚本需要）
- 具体依赖见各 Skill 的 `SKILL.md`