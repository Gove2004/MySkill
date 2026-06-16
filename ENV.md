# ENV 规范

Skill 需要敏感配置（密钥、token、凭据）时，遵循此规范。

## 三文件约定

| 文件 | 用途 | 入 git |
|------|------|--------|
| `.env.example` | 配置模板，占位值，告诉用户有哪些配置项 | ✅ 入 |
| `.env` | 真实凭据，从 `.env.example` 复制后填入 | ❌ 不入 |
| `scripts/*.py` | 通过 `_load_env()` 读取 `.env`，提供默认值回退 | ✅ 入 |

## .env.example 格式

```env
# 注释说明这项是干什么的
KEY_NAME=your_value_here
```

## _load_env() 模板

直接复制到脚本顶部，去掉不需要的字段即可：

```python
import os

def _load_env():
    """从 Skill 根目录 .env 加载配置，返回 dict。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, "..", ".env")
    env = {}
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip("\"'")
    except FileNotFoundError:
        pass
    return env

_env = _load_env()
MY_KEY = _env.get("MY_KEY", "默认值")
```

## 已有 Skill 参考

| Skill | 配置项 |
|-------|--------|
| `pdf-to-markdown/` | `MINERU_TOKEN` |
| `send-email-skill/` | `SMTP_SERVER`, `SMTP_PORT`, `SENDER_EMAIL`, `AUTH_CODE` |

## 新增 Skill 步骤

1. 复制此 `ENV.md` 中的 `_load_env()` 模板到你的脚本
2. 创建 `.env.example`，列出所有配置项 + 占位值
3. 复制 `.env.example` → `.env`，填入真实值
4. 确认 `.gitignore` 已排除 `.env`（不排除 `.env.example`）