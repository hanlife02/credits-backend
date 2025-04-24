import random
import string
import smtplib
# from typing import List, Optional  # 未使用
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


def generate_verification_code(length: int = 6) -> str:
    """Generate a random verification code"""
    return ''.join(random.choices(string.digits, k=length))


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
) -> bool:
    """
    Send an email using the configured SMTP server
    """
    message = MIMEMultipart()
    message["From"] = settings.FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(html_content, "html"))

    try:
        # For development, print the email
        print(f"\n--- EMAIL ---\nTo: {to_email}\nSubject: {subject}\nContent: {html_content}\n--- END EMAIL ---\n")

        # Actually send emails
        # QQ邮箱使用SSL而不是TLS
        if settings.SMTP_HOST == "smtp.qq.com":
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_verification_email(to_email: str, code: str) -> bool:
    """
    Send a verification email with the provided code
    """
    subject = "邮箱验证 - 毕业学分审查系统"
    html_content = f"""
    <html>
        <body>
            <h2>邮箱验证</h2>
            <p>感谢您注册毕业学分审查系统。</p>
            <p>您的验证码是：<strong>{code}</strong></p>
            <p>此验证码将在15分钟后过期。</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, html_content)


def send_password_reset_email(to_email: str, code: str) -> bool:
    """
    Send a password reset email with the provided code
    """
    subject = "密码重置 - 毕业学分审查系统"
    html_content = f"""
    <html>
        <body>
            <h2>密码重置</h2>
            <p>您已申请重置毕业学分审查系统的密码。</p>
            <p>您的验证码是：<strong>{code}</strong></p>
            <p>此验证码将在15分钟后过期。</p>
            <p>如果您没有申请重置密码，请忽略此邮件。</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, html_content)
