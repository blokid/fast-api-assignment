import logging

from fastapi_mail import FastMail, MessageSchema

from app.core.config import AppSettings, get_app_settings
from app.models import OrganizationInvite

logger = logging.getLogger(__name__)


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


async def send_invitation_email(
    invite: OrganizationInvite,
    token: str,
) -> None:
    app_settings: AppSettings = get_app_settings()
    invitation_link = f"{app_settings.frontend_url}/invite?token={token}"
    organization = await invite.awaitable_attrs.organization
    message = MessageSchema(
        subject=f"You've been invited to join the organization {organization.name}",
        recipients=[invite.email],
        body=f"Please accept the invitation by clicking the link below:\n\n{invitation_link}",
        subtype="plain",
    )
    fm = FastMail(app_settings.mail_config)
    await fm.send_message(message)
    logger.info(f"Invitation mail sent to {invite.email}!")
