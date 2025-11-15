from email.message import EmailMessage

import aiosmtplib


async def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = "test@example.com"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(message, hostname="maildev", port=1025)
