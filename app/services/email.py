import random
import string
import smtplib
import logging
import traceback
import time
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate

from app.core.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_verification_code(length: int = 6) -> str:
    """Generate a random verification code"""
    return ''.join(random.choices(string.digits, k=length))


def save_email_to_file(to_email: str, subject: str, html_content: str, code: str = None) -> bool:
    """
    将邮件保存到文件中，用于开发环境测试
    """
    try:
        # 生成唯一的邮件ID用于跟踪
        timestamp = int(time.time())
        email_id = f"{timestamp}_{to_email}_{subject[:10]}"

        # 创建邮件目录
        email_dir = os.path.join("logs", "emails")
        if not os.path.exists(email_dir):
            os.makedirs(email_dir)

        # 创建邮件文件名
        filename = f"{email_dir}/{to_email.replace('@', '_')}_{timestamp}.json"

        # 构建邮件内容
        email_data = {
            "id": email_id,
            "to": to_email,
            "subject": subject,
            "content": html_content,
            "timestamp": timestamp,
            "code": code
        }

        # 写入文件
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(email_data, f, ensure_ascii=False, indent=2)

        logger.info(f"[{email_id}] 邮件已保存到文件: {filename}")
        return True
    except Exception as e:
        logger.error(f"保存邮件到文件失败: {str(e)}")
        return False


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    max_retries: int = 3,
    code: str = None,  # 可选参数，用于记录验证码
) -> bool:
    """
    Send an email using the configured SMTP server with retry mechanism
    """
    # 创建邮件消息
    message = MIMEMultipart()
    message["From"] = settings.FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = f"<{int(time.time())}@{settings.SMTP_HOST.split('.')[-2]}.com>"

    message.attach(MIMEText(html_content, "html"))

    # 生成唯一的邮件ID用于跟踪
    email_id = f"{int(time.time())}_{to_email}_{subject[:10]}"

    # 记录邮件内容（开发环境）
    logger.info(f"\n--- EMAIL [{email_id}] ---\nTo: {to_email}\nSubject: {subject}\nContent: {html_content}\n--- END EMAIL ---\n")

    # 记录SMTP配置信息（不包含密码）
    logger.info(f"[{email_id}] SMTP配置: Host={settings.SMTP_HOST}, Port={settings.SMTP_PORT}, User={settings.SMTP_USER}")

    # 开发环境模式：将邮件保存到文件而不是实际发送
    # 检查环境变量或配置文件中的标志
    if os.environ.get("EMAIL_DEV_MODE", "false").lower() == "true":
        logger.info("开发环境模式: 邮件将保存到文件而不是实际发送")
        return save_email_to_file(to_email, subject, html_content, code)

    # 实现重试机制
    for attempt in range(max_retries):
        try:
            logger.info(f"[{email_id}] 尝试发送邮件 (尝试 {attempt+1}/{max_retries})")

            # QQ邮箱使用SSL而不是TLS
            if settings.SMTP_HOST == "smtp.qq.com":
                logger.info(f"[{email_id}] 使用SSL连接QQ邮箱SMTP服务器")
                # 注意：这里我们不使用with语句，手动关闭连接
                server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
                server.set_debuglevel(1)
                logger.info(f"[{email_id}] 尝试登录SMTP服务器")
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                logger.info(f"[{email_id}] 登录成功，发送邮件")
                server.send_message(message)
                logger.info(f"[{email_id}] 邮件发送成功")
                # 手动关闭连接，忽略可能的错误
                try:
                    server.quit()
                except Exception as close_error:
                    logger.warning(f"[{email_id}] 关闭SMTP连接时出现非致命错误: {close_error}")
            else:
                logger.info(f"[{email_id}] 使用TLS连接SMTP服务器: {settings.SMTP_HOST}")
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
                server.set_debuglevel(1)
                logger.info(f"[{email_id}] 启动TLS加密")
                server.starttls()
                logger.info(f"[{email_id}] 尝试登录SMTP服务器")
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                logger.info(f"[{email_id}] 登录成功，发送邮件")
                server.send_message(message)
                logger.info(f"[{email_id}] 邮件发送成功")
                # 手动关闭连接，忽略可能的错误
                try:
                    server.quit()
                except Exception as close_error:
                    logger.warning(f"[{email_id}] 关闭SMTP连接时出现非致命错误: {close_error}")

            # 如果成功发送，返回true
            return True

        except Exception as e:
            # 记录错误
            logger.error(f"[{email_id}] 发送邮件失败 (尝试 {attempt+1}/{max_retries}): {str(e)}")
            logger.error(traceback.format_exc())

            # 如果这是最后一次尝试，尝试保存到文件
            if attempt == max_retries - 1:
                logger.error(f"[{email_id}] 所有重试尝试失败，无法发送邮件到 {to_email}")
                logger.info(f"[{email_id}] 尝试将邮件保存到文件...")
                return save_email_to_file(to_email, subject, html_content, code)

            # 否则等待一段时间后重试
            wait_time = (attempt + 1) * 2  # 指数退避：2秒，然后4秒，然后6秒
            logger.info(f"[{email_id}] 等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)

    # 如果所有重试都失败，返回false
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
    return send_email(to_email, subject, html_content, code=code)


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
    return send_email(to_email, subject, html_content, code=code)
