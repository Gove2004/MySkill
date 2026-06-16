# CLAUDE.md

个人 Claude Code 技能集合。每个子目录是一个可安装的 Skill，包含 `SKILL.md`（技能定义与指令）及配套资源。

## 目录结构

```
MySkill/
├── send-email-skill/       # SMTP 邮件发送
├── godot-procedural-kit/   # Godot 程序化内容工具包
├── make-tutorial/          # 中文教程体系生成
├── pdf-to-markdown/        # 文档转 Markdown（MinerU API）
├── CLAUDE.md
├── README.md
├── distribute.bat          # 一键分发脚本
└── .gitignore
```

## Skill 约定

每个 Skill 目录标准结构：

```text
skill-name/
├── SKILL.md          # 必需：技能元数据（YAML frontmatter）与详细指令
├── .env.example      # 必需如有敏感配置：模板（占位值），入 git
├── .env              # 可选如有敏感配置：真实凭据（已 gitignore）
├── scripts/          # 可选：可执行脚本
├── references/       # 可选：参考文档、模板、示例
└── bundled_addons/   # 可选：内置第三方资源
```

### SKILL.md 格式

```markdown
---
name: skill-name
description: 简短描述，用于触发匹配。包含触发关键词。
---

# Skill 标题

详细指令...
```

### 设计原则

- **独立可安装**：每个 Skill 是一个自包含目录，可复制到其他项目
- **脚本优先**：Python 脚本收在 `scripts/`，用绝对路径引用
- **敏感信息隔离**：密钥、token、凭据一律存入 `.env`，不硬编码。同时提供 `.env.example` 模板（占位值）供参考，`.env.example` 入 git，`.env` 不入。
- **引用文件**：长篇参考内容放 `references/`，SKILL.md 通过表格索引

## 环境依赖

部分 Skill 脚本依赖 Python 第三方库：

- `send-email-skill`：标准库，无额外依赖
- `pdf-to-markdown`：`requests`（MinerU API 调用）

## 注意事项

- `pdf-to-markdown/.env` 包含 MinerU API token，已在 `.gitignore` 排除
- `send-email-skill/.env` 包含 SMTP 凭据，已在 `.gitignore` 排除
- 各 Skill 的 `.env.example` 为配置模板，入 git，安装后复制为 `.env` 填入真实值
- `Garbage/` 目录为无关数据，已在 `.gitignore` 排除