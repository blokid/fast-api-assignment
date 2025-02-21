# services/email_service.py

from functools import lru_cache
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import get_app_settings
from app.core.constant import SENDER_EMAIL, EMAIL_VERIFICATION_ROUTE


class EmailService:
    def __init__(self):
        self.settings = get_app_settings()
        self.smtp_host = self.settings.smtp_host
        self.smtp_port = self.settings.smtp_port
        self.smtp_username = self.settings.smtp_username
        self.smtp_password = self.settings.smtp_password

    def send_email(self, to: str, subject: str, html_content: str):
        """Send email using SMTP."""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = SENDER_EMAIL
            message["To"] = to

            part = MIMEText(html_content, "html")
            message.attach(part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(SENDER_EMAIL, to, message.as_string())

            return {"message": "Email sent successfully"}
        except Exception as e:
            raise RuntimeError(f"Failed to send email: {e}")

    def get_verification_email_content(
        self, verification_url: str, verification_token: str, username: str
    ) -> str:
        """Generate email content for email verification."""
        return f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h4>Hi {username}!, Welcome onboard</h4>
            <p>Thank you for signing up. To verify your email, please paste and run the following command in your linux/unix terminal:</p>
            <pre style="background-color:#f4f4f4; padding:10px; border-radius:5px;">
curl -X POST "{verification_url}" \\
-H "Content-Type: application/json" \\
-d '{{"verification_token": "{verification_token}"}}'
            </pre>
            <p>If you didn’t request this, please ignore this email.</p>
          </body>
        </html>
        """

    def send_verification_email(
        self, email: str, verification_token: str, username: str
    ):
        """Send verification email with a verification link."""
        email_verification_url = (
            self.settings.email_verification_base_url + EMAIL_VERIFICATION_ROUTE
        )
        self.send_email(
            to=email,
            subject="Verify your email",
            html_content=self.get_verification_email_content(
                verification_url=email_verification_url,
                verification_token=verification_token,
                username=username,
            ),
        )


@lru_cache()
def get_email_service() -> EmailService:
    """Singleton Dependency Provider for EmailService."""
    return EmailService()
