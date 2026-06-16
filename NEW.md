# NEW.md — 新建 Skill 指南

为 MySkill 项目创建新的 Claude Code Skill 的标准流程和规范。

## 快速开始

```text
1. 明确 Skill 做什么、何时触发
2. 按模板创建目录和 SKILL.md
3. 有敏感配置 → 参考 ENV.md 加 .env.example
4. 有脚本 → 放 scripts/
5. 有长篇参考 → 放 references/
```

## 目录模板

```
my-new-skill/
├── SKILL.md          # 必需：元数据 + 指令
├── .env.example      # 如有密钥/token（入 git）
├── .env              # 真实凭据（不入 git）
├── scripts/          # 可选：Python 脚本
├── references/       # 可选：参考文档
└── bundled_addons/   # 可选：第三方资源
```

## SKILL.md 模板

```markdown
---
name: my-new-skill
description: 简短描述。包含触发关键词和适用场景。例如："Use this skill when the user asks to X, mentions Y, or needs to Z. Triggers on '做X', 'Y操作'."
---

# Skill 标题

简要说明这个 Skill 做什么。

## 触发条件

（可选）列出具体的触发短语或场景，帮助 Claude 判断何时使用。

## 使用方式

说明 Claude 应如何使用这个 Skill —— 执行什么脚本、读取什么参考文件、输出什么格式。

## 参数 / 配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| ... | ... | ... |

## 注意事项

- 限制、边界情况、已知问题
```

## 编写 SKILL.md 要点

### description（触发机制）

description 是 Claude 决定是否调用 Skill 的**唯一依据**。写好的原则：

- **具体**：不止说做什么，还说什么时候用。包含触发短语（中英文都可以）。
- **主动**：偏"pushy"一点，宁可多触发不少触发。Claude 倾向于不触发 Skill。
- **区分度**：如果和其他 Skill 有重叠，描述要明确各自边界。

```yaml
# ✅ 好
description: Convert PDF files to Markdown using MinerU API. Use whenever the user needs to read a PDF, extract text from a PDF, or asks about PDF contents. Also handles Word, PPT, Excel, images. Triggers on "帮我读PDF", "解析文档".

# ❌ 差
description: PDF to Markdown converter.
```

### 指令正文

- **用祈使句**，直接告诉 Claude 怎么做。
- **解释为什么**，而不只是堆 MUST / ALWAYS。模型需要理解意图才能应对变化。
- **给出可复制的代码**而不是抽象描述。
- **示例**比规则更有用。有输入/输出示例时，格式参考 `skill-creator` 的写法。
- **<500 行**，太长了就拆到 `references/`。

### 触发条件怎么写

description 写得好，这一步可以省略。但如果有容易混淆的场景（和另一个 Skill 重叠），可以在正文加一句：

```markdown
## 何时使用 / 何时不使用

**使用：**
- 用户要读取 PDF 内容

**不使用：**
- 用户要创建或编辑 PDF（那是另一个工具的事）
```

## 敏感配置

如果 Skill 需要 API token、密码等敏感信息：

1. 创建 `.env.example`（模板，入 git）
2. 复制为 `.env`（真实值，不入 git）
3. 脚本中用 `_load_env()` 读取

详见 **ENV.md**，里面有可直接复制的 `_load_env()` 模板。

## 脚本规范

- 用 Python，标准库优先，减少依赖
- 收在 `scripts/` 目录
- 每个 Skill 自包含，**不跨 Skill 共享代码**
- 用绝对路径或相对于脚本自身的路径定位资源：

```python
script_dir = os.path.dirname(os.path.abspath(__file__))
skill_root = os.path.join(script_dir, "..")
```

## 命名约定

| 项 | 规范 | 示例 |
|----|------|------|
| 目录名 | 小写 + 连字符 | `pdf-to-markdown` |
| SKILL.md name | 同目录名 | `pdf-to-markdown` |
| 章节文件 | `01-标题.html` | `01-iterators.html` |
| 脚本 | 小写 + 下划线 | `send_mail.py` |

## 参考现有 Skill

| Skill | 特点 | 可参考 |
|-------|------|--------|
| `pdf-to-markdown/` | 有 .env、有 scripts/、有 references/ | 完整示例 |
| `send-email-skill/` | 有 .env、有 scripts/、简洁 | 简单 Skill 模板 |
| `make-tutorial/` | 只有 SKILL.md + references/ | 纯指令型 Skill |
| `godot-procedural-kit/` | 有 bundled_addons/ | 带第三方资源的 Skill |

## 新建 Checklist

- [ ] 目录名 = SKILL.md 的 `name` 字段
- [ ] `description` 包含触发词和适用场景
- [ ] 正文用祈使句，解释为什么
- [ ] 有敏感配置 → `.env.example` + 脚本中 `_load_env()`（参考 `ENV.md`）
- [ ] 脚本自包含，不依赖其他 Skill
- [ ] `.gitignore` 已排除 `.env`