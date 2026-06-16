import os
import sys
import json
import smtplib
import argparse
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header


def _load_env():
    """Load SMTP config from .env file (relative to this script)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, "..", ".env"),   # skill root
        os.path.join(script_dir, ".env"),          # scripts/
    ]
    env = {}
    for env_path in candidates:
        try:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
        except FileNotFoundError:
            continue
    return env


_env = _load_env()
smtp_server = _env.get("SMTP_SERVER", "smtp.qq.com")
smtp_port = int(_env.get("SMTP_PORT", "465"))
sender_email = _env.get("SENDER_EMAIL", "")
auth_code = _env.get("AUTH_CODE", "")

def send_email(to_addrs, subject, body, is_html=False, attachments=None):
    if not sender_email or not auth_code:
        print("Error: sender_email or auth_code is missing in config.json")
        sys.exit(1)

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = Header(subject, "utf-8")

    content_type = "html" if is_html else "plain"
    msg.attach(MIMEText(body, content_type, "utf-8"))

    if attachments:
        for fpath_str in attachments:
            fpath = Path(fpath_str)
            if not fpath.exists():
                print(f"Warning: Attachment not found: {fpath}")
                continue
            with open(fpath, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{fpath.name}"')
            msg.attach(part)

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, auth_code)
            server.sendmail(sender_email, to_addrs, msg.as_string())
        print(f"Successfully sent email to {', '.join(to_addrs)}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send an email directly via SMTP")
    parser.add_argument("--to", required=True, help="Comma-separated list of recipients")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", required=True, help="Email body")
    parser.add_argument("--html", action="store_true", help="Send body as HTML")
    parser.add_argument("--attachment", nargs="+", help="Paths to attachments")
    
    args = parser.parse_args()
    
    to_list = [email.strip() for email in args.to.split(",") if email.strip()]
    send_email(to_list, args.subject, args.body, args.html, args.attachment)
