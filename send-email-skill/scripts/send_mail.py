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

# 读取全局配置
smtp_server = "smtp.qq.com"
smtp_port = 465
sender_email = "3425519400@qq.com"
auth_code = "utiihlwzsdibdbhg"

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
