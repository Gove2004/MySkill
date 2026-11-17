---
name: send-email
description: Send emails directly via SMTP. Use when the user asks to "send an email", "email this file", "notify via email", "发邮件", "发封邮件", "邮件通知", "把文件发到我邮箱", or needs to deliver a file/message through email. Supports HTML body and attachments.
---

# Send Email

通过 SMTP 直接发送邮件,无需本地 HTTP 服务。脚本位于 `scripts/send_mail.py`,自动从 `.env` 读取 SMTP 凭据。

## 配置

复制 `.env.example` 为 `.env`,填入真实值:

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SMTP_SERVER` | SMTP 服务器地址 | `smtp.qq.com` |
| `SMTP_PORT` | SMTP 端口 | `465` |
| `SENDER_EMAIL` | 发件人邮箱(必填) | — |
| `AUTH_CODE` | 邮箱授权码(必填,非登录密码) | — |
| `DEFAULT_TO` | 默认收件人,未传 `--to` 时使用(逗号分隔多个) | — |

## 用法

```bash
python scripts/send_mail.py --to "recipient@example.com" --subject "主题" --body "正文"
```

`--to` 可省略 —— 省略时回退到 `.env` 的 `DEFAULT_TO`;两者都没有则报错。

## 参数

| 参数 | 说明 | 必填 |
|------|------|------|
| `--to` | 收件人,逗号分隔多个。省略则用 `DEFAULT_TO` | 否 |
| `--subject` | 邮件主题 | 是 |
| `--body` | 邮件正文 | 是 |
| `--html` | 把 `--body` 当 HTML 渲染 | 否 |
| `--attachment` | 附件路径,可多个 | 否 |

## 示例

**纯文本邮件:**

```bash
python scripts/send_mail.py --to "a@x.com" --subject "任务完成" --body "任务已成功完成。"
```

**HTML 邮件 + 附件:**

```bash
python scripts/send_mail.py --to "a@x.com" --subject "日报" \
  --body "<h1>日报</h1><p>详见附件。</p>" --html --attachment "C:\path\to\report.md"
```

**用默认收件人(已在 .env 配 `DEFAULT_TO`):**

```bash
python scripts/send_mail.py --subject "提醒" --body "该上线了。"
```

## 注意事项

- 始终基于本 Skill 根目录解析 `scripts/send_mail.py` 的绝对路径。
- 用户刚生成的文件要随邮件发出时,用 `--attachment`。
- `AUTH_CODE` 是邮箱授权码(QQ/163 等),不是登录密码。
- 多个收件人用逗号分隔传给 `--to`。
