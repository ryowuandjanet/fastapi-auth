import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from dotenv import load_dotenv
import os
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class EmailConfig:
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_SERVER = os.getenv('MAIL_SERVER')

async def send_reset_password_email(email: str, token: str):
    try:
        # 創建郵件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header('Password Reset Request', 'utf-8')
        msg['From'] = EmailConfig.MAIL_USERNAME
        msg['To'] = email

        # 重置連結
        reset_link = f"http://localhost:8000/reset-password?token={token}"

        # HTML 內容
        html_content = f"""
        <html>
            <head>
                <meta charset="utf-8">
            </head>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hi,</p>
                <p>We received a request to reset your password. Click the link below to reset it:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>If you didn't request this, please ignore this email.</p>
                <p>The link will expire in 24 hours.</p>
                <br>
                <p>Best regards,</p>
                <p>Your App Team</p>
            </body>
        </html>
        """

        # 添加 HTML 內容
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        # 連接到 SMTP 服務器
        server = smtplib.SMTP(EmailConfig.MAIL_SERVER, EmailConfig.MAIL_PORT)
        server.starttls()
        server.login(EmailConfig.MAIL_USERNAME, EmailConfig.MAIL_PASSWORD)

        # 發送郵件
        server.sendmail(EmailConfig.MAIL_USERNAME, email, msg.as_string())
        server.quit()

        logger.info(f"Successfully sent email to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        logger.exception("Detailed error:")
        return False
