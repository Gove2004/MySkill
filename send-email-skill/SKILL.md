---
name: send-email-skill
description: Use this skill to send emails directly via SMTP. Trigger this when the user asks to "send an email", "email this file", "notify via email", or "发邮件".
---

# Send Email Skill

This skill allows you to send emails directly using SMTP, bypassing any local HTTP API services.

## How to use

You have access to a bundled Python script `scripts/send_mail.py` that handles the SMTP communication.

To send an email, execute the script using Python:

```bash
python /path/to/skill/scripts/send_mail.py --to "recipient@example.com" --subject "Your Subject" --body "Your email body"
```

### Arguments:
- `--to`: Comma-separated list of recipient email addresses. If the user doesn't specify, default to `3425519400@qq.com`.
- `--subject`: The subject of the email.
- `--body`: The body content of the email.
- `--html`: (Optional) Flag to indicate the body should be rendered as HTML.
- `--attachment`: (Optional) One or more file paths to attach to the email.

### Examples

**Example 1: Sending a simple text email**
```bash
python /path/to/skill/scripts/send_mail.py --to "3425519400@qq.com" --subject "Task Completed" --body "The task has been successfully completed."
```

**Example 2: Sending an HTML email with an attachment**
```bash
python /path/to/skill/scripts/send_mail.py --to "3425519400@qq.com" --subject "Daily Report" --body "<h1>Report</h1><p>See attached.</p>" --html --attachment "C:\path\to\report.md"
```

## Important Notes
- ALWAYS resolve the absolute path to `scripts/send_mail.py` based on the skill's base directory.
- If the user asks to send a file they just generated, use the `--attachment` flag.
- The script automatically reads SMTP credentials from `.env` (see `.env.example` for required keys).
