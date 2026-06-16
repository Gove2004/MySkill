# MySkill — 个人 Claude Code 技能集合

四个独立可安装的 Claude Code Skill，覆盖文档处理、内容生成、游戏开发和工具集成。

## 技能列表

| 技能 | 说明 | 触发方式 |
|------|------|----------|
| **pdf-to-markdown** | PDF/Word/PPT/Excel/图片 → Markdown，基于 MinerU API，支持表格、公式、多栏布局 | `帮我读这个PDF`、`解析这个文档` |
| **make-tutorial** | 生成专业级中文教程（多文件 HTML 站点），含代码高亮、交互组件、多种主题风格 | `做教程`、`写课程`、`整理成教程` |
| **godot-procedural-kit** | Godot 程序化内容工具包 — `_draw()` 几何绘制、程序化粒子/音效、网格地图生成 | Godot 项目中的程序化生成需求 |
| **send-email-skill** | 直接通过 SMTP 发送邮件，支持 HTML 正文和附件 | `发邮件`、`send an email` |

## 安装

将技能目录复制到 `~/.claude/skills/` 或项目的 `.claude/skills/` 下即可。

```bash
# 安装单个技能
cp -r MySkill/pdf-to-markdown ~/.claude/skills/

# 或安装全部
cp -r MySkill/*/ ~/.claude/skills/
```

## 环境要求

- Python 3.x（`pdf-to-markdown`、`send-email-skill` 需要）
- `pdf-to-markdown` 额外依赖：`pip install requests`
- `send-email-skill` 使用 Python 标准库，无需额外安装

## 目录结构

```
MySkill/
├── send-email-skill/
│   ├── SKILL.md
│   ├── .env.example
│   └── scripts/send_mail.py
├── godot-procedural-kit/
│   ├── SKILL.md
│   ├── references/
│   └── bundled_addons/    # gdfxr, sound_manager, phantom_camera
├── make-tutorial/
│   ├── SKILL.md
│   └── references/
├── pdf-to-markdown/
│   ├── SKILL.md
│   ├── scripts/parse_pdf.py
│   ├── references/
│   ├── .env.example
│   └── .env               # MinerU token（不入库）
├── CLAUDE.md
├── README.md
├── ENV.md                  # .env 规范
├── NEW.md                  # 新建 Skill 指南
├── distribute.bat          # 一键分发脚本
└── .gitignore
```

## 技能详情

### pdf-to-markdown

支持格式：PDF、DOC/DOCX、PPT/PPTX、XLS/XLSX、PNG/JPG/WebP、HTML

- **Precision API**（默认）：最佳质量，支持表格/公式识别，限制 200MB/200页
- **Agent API**（回退）：轻量快速，无需 token，限制 10MB/20页

```bash
python scripts/parse_pdf.py --pdf document.pdf
python scripts/parse_pdf.py --pdf image.png --ocr --language en
```

### make-tutorial

生成可直接在浏览器中打开的多文件 HTML 教程站点：

- 6 种主题风格自动适配（技术/数学/科学/设计/人文/商业）
- 代码语法高亮（Prism.js）+ 一键复制
- 可折叠章节、提示框、标签页、步骤流程图
- 专业级内容：实战示例、故障排查、最佳实践、练习题

### godot-procedural-kit

面向 Godot 引擎的程序化内容生成方案：

- `_draw()` 几何绘制与几何 UI
- 脚本驱动的粒子系统
- 基于 gdfxr 的程序化音效
- 网格地图与结构生成
- 内置可直接复制的 addon：gdfxr、sound_manager、phantom_camera

### send-email-skill

```bash
python scripts/send_mail.py --to "user@example.com" --subject "标题" --body "正文"
python scripts/send_mail.py --to "user@example.com" --subject "报告" --body "<h1>报告</h1>" --html --attachment report.pdf
```

默认收件人为 `3425519400@qq.com`，SMTP 通过 QQ 邮箱发送。