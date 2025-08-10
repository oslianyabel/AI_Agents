import asyncio
import base64
import json
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

from aiosmtplib import SMTP
from dotenv import load_dotenv

load_dotenv()


def get_gmail_connection():
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_PASSWORD"))
        return server
    except Exception as e:
        return e


async def get_async_gmail_connection():
    try:
        smtp = SMTP(hostname="smtp.gmail.com", port=465, use_tls=True)
        await smtp.connect()
        await smtp.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_PASSWORD"))
        return smtp
    except Exception as e:
        return e


def send_email(
    to: str,
    subject: str,
    body: str,
    is_html: bool = False,
    attachments: Optional[List[Dict]] = None,
) -> str:
    try:
        # Create message
        msg = MIMEMultipart()
        msg["From"] = os.getenv("GMAIL_USER")
        msg["To"] = to
        msg["Subject"] = subject

        # Attach body
        if is_html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        # Handle attachments
        if attachments:
            for attachment in attachments:
                if "filename" not in attachment:
                    continue

                file_path = attachment["filename"]
                if not os.path.exists(file_path):
                    return json.dumps(
                        {"status": "error", "message": f"File not found: {file_path}"}
                    )
                with open(file_path, "rb") as f:
                    file_content = base64.b64encode(f.read()).decode("utf-8")
                attachment["content"] = file_content

                file_content = base64.b64decode(attachment["content"])
                part = MIMEApplication(file_content, Name=attachment["filename"])
                part["Content-Disposition"] = (
                    f'attachment; filename="{attachment["filename"]}"'
                )
                msg.attach(part)

        # Send email
        server = get_gmail_connection()
        if isinstance(server, Exception):
            return json.dumps(
                {"status": "error", "message": f"SMTP connection error: {server}"}
            )

        server.send_message(msg)
        server.quit()

        return json.dumps({"status": "success", "message": "Email sent successfully"})

    except Exception as e:
        return json.dumps(
            {"status": "error", "message": f"Failed to send email: {str(e)}"}
        )


async def async_send_email(
    to: str,
    subject: str,
    body: str,
    is_html: bool = False,
    attachments: Optional[List[Dict]] = None,
) -> str:
    try:
        # Create message
        msg = MIMEMultipart()
        msg["From"] = os.getenv("GMAIL_USER")
        msg["To"] = to
        msg["Subject"] = subject

        # Attach body
        if is_html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        # Handle attachments
        if attachments:
            for attachment in attachments:
                if "filename" not in attachment:
                    continue

                file_path = attachment["filename"]
                if not os.path.exists(file_path):
                    return json.dumps(
                        {"status": "error", "message": f"File not found: {file_path}"}
                    )
                with open(file_path, "rb") as f:
                    file_content = base64.b64encode(f.read()).decode("utf-8")
                attachment["content"] = file_content

                file_content = base64.b64decode(attachment["content"])
                part = MIMEApplication(file_content, Name=attachment["filename"])
                part["Content-Disposition"] = (
                    f'attachment; filename="{attachment["filename"]}"'
                )
                msg.attach(part)

        # Send email asynchronously
        smtp = await get_async_gmail_connection()
        if isinstance(smtp, Exception):
            return json.dumps(
                {"status": "error", "message": f"SMTP connection error: {smtp}"}
            )

        await smtp.send_message(msg)
        await smtp.quit()

        return json.dumps({"status": "success", "message": "Email sent successfully"})

    except Exception as e:
        return json.dumps(
            {"status": "error", "message": f"Failed to send email: {str(e)}"}
        )


if __name__ == "__main__":
    print(
        send_email(
            to="oslianyabel@outlook.com",
            subject="Test Email with Attachment",
            body="This email contains an attachment.",
            attachments=[
                {
                    "filename": "notes.txt",
                }
            ],
        )
    )

    async def test_async():
        result = await async_send_email(
            to="oslianyabel@outlook.com",
            subject="Test Async Email with Attachment",
            body="This email contains an attachment (sent asynchronously).",
            attachments=[
                {
                    "filename": "notes.txt",
                }
            ],
        )
        print(result)

    asyncio.run(test_async())
