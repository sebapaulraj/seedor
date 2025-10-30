import aiosmtplib
from email.mime.text import MIMEText
from app.core.config import settings

async def send_verification_email(to_email: str, token: str):
    """Send verification email with secure token."""
    verify_link = f"{settings.FRONTEND_VERIFY_URL}?token={token}"

    subject = "Verify your email address"
    body = f"""
    Hi,

    Please verify your email by clicking the link below:
    {verify_link}

    This link will expire in 15 minutes.

    Regards,
    Your App Team
    """

    msg = MIMEText(body)
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject

    await aiosmtplib.send(
        msg,
        hostname=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        start_tls=True,
        username=settings.EMAIL_USER,
        password=settings.EMAIL_PASS,
    )
