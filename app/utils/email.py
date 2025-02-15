from fastapi_mail import FastMail, MessageSchema

from app.core.config import AppSettings, get_app_settings


async def send_verification_email(email: str, token: str) -> None:
    app_settings: AppSettings = get_app_settings()
    verification_link = f"{app_settings.frontend_url}/verify?token={token}"
    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"Please verify your email by clicking the link below:\n\n{verification_link}",
        subtype="plain",
    )
    fm = FastMail(app_settings.mail_config)
    await fm.send_message(message)
