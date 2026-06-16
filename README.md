# MySkill

个人 Claude Code 技能集合。每个子目录是一个可独立安装的 Skill。

## 技能

| 技能 | 说明 |
|------|------|
| `kb/` | 本地 RAG 知识库 — 语义检索、增量索引、智能删除 |
| `pdf-to-markdown/` | 文档转 Markdown（PDF/Word/PPT/Excel/图片），基于 MinerU API |
| `make-tutorial/` | 专业级中文教程生成，输出多文件 HTML 站点 |
| `godot-procedural-kit/` | Godot 4 程序化内容（几何绘制、粒子、音效、地图、特效） |
| `send-email-skill/` | SMTP 邮件发送，支持 HTML 和附件 |

## 快速开始

### 安装

将技能目录复制到 `~/.claude/skills/`，如有 `.env.example` 则复制为 `.env` 填入真实配置：

```bash
cp -r <skill-name> ~/.claude/skills/
cp ~/.claude/skills/<skill-name>/.env.example ~/.claude/skills/<skill-name>/.env
```

Windows 用户可双击 `distribute.bat` 一键分发全部技能。

### 新建技能

参考 [NEW.md](NEW.md)。

## 规范

- **[ENV.md](ENV.md)** — 敏感配置：`.env.example` + `.env` + `_load_env()`
- **[NEW.md](NEW.md)** — 新建 Skill 模板、命名约定、Checklist

## 要求

- Python 3（部分 Skill 脚本需要）