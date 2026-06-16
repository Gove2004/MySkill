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
└── .gitignore
```

## Skill 约定

每个 Skill 目录标准结构：

```
skill-name/
├── SKILL.md          # 必需：技能元数据（YAML frontmatter）与详细指令
├── scripts/          # 可选：可执行脚本
├── references/       # 可选：参考文档、模板、示例
├── bundled_addons/   # 可选：内置第三方资源
└── .env              # 可选：敏感配置（已 gitignore）
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
- **敏感信息隔离**：密钥、token 放 `.env`，不硬编码（存量代码暂不重构）
- **引用文件**：长篇参考内容放 `references/`，SKILL.md 通过表格索引

## 环境依赖

部分 Skill 脚本依赖 Python 第三方库：

- `send-email-skill`：标准库，无额外依赖
- `pdf-to-markdown`：`requests`（MinerU API 调用）

## 注意事项

- `pdf-to-markdown/.env` 包含 MinerU API token，已在 `.gitignore` 排除
- `send-email-skill/scripts/send_mail.py` 当前硬编码了 SMTP 凭据（需后续改为读配置文件）
- `Garbage/` 目录为无关数据，已在 `.gitignore` 排除