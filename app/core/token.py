from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from pydantic import ValidationError

from app.models import OrganizationInvite, User
from app.models.website import WebsiteInvite
from app.schemas.token import (
    TokenBase,
    TokenInvite,
    TokenInviteWebsite,
    TokenUser,
    TokenVerify,
)
from app.schemas.user import InvitationTokenData, UserTokenData, VerificationTokenData

TOKEN_TYPE = "bearer"
JWT_SUBJECT = "access"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_token(
    *,
    content: dict[str, str],
    secret_key: str,
    expires_delta: timedelta | None = timedelta(minutes=15),
):
    to_encode = content.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update(TokenBase(exp=expire, sub=JWT_SUBJECT).model_dump())

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_token_for_user(user: User, secret_key: str) -> UserTokenData:
    token_user_dict = TokenUser(
        id=user.id, username=user.username, email=user.email
    ).model_dump()
    created_token = create_token(
        content=token_user_dict,
        secret_key=secret_key,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return UserTokenData(access_token=created_token, token_type=TOKEN_TYPE)


def create_verification_token(user: User, secret_key: str) -> VerificationTokenData:
    verification_token_dict = TokenVerify(email=user.email).model_dump()
    created_token = create_token(
        content=verification_token_dict,
        secret_key=secret_key,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return VerificationTokenData(token=created_token)


def create_org_invitation_token(
    invite: OrganizationInvite, secret_key: str
) -> InvitationTokenData:
    invitation_token_dict = TokenInvite(
        organization_id=invite.organization_id, email=invite.email
    ).model_dump()
    created_token = create_token(
        content=invitation_token_dict,
        secret_key=secret_key,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return InvitationTokenData(token=created_token)


def create_website_invitation_token(
    invite: WebsiteInvite, secret_key: str
) -> InvitationTokenData:
    invitation_token_dict = TokenInviteWebsite(
        website_id=invite.website_id, email=invite.email
    ).model_dump()
    created_token = create_token(
        content=invitation_token_dict,
        secret_key=secret_key,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return InvitationTokenData(token=created_token)


def get_user_from_token(token: str, secret_key: str) -> str:
    try:
        decoded_user = jwt.decode(token, secret_key, algorithms=ALGORITHM)
        return TokenUser(**decoded_user)

    except JWTError as decode_error:
        raise ValueError("unable to decode") from decode_error
    except ValidationError as validation_error:
        raise ValueError("invalid token") from validation_error


def get_email_from_token(token: str, secret_key: str) -> TokenVerify:
    try:
        decoded_email = jwt.decode(token, secret_key, algorithms=ALGORITHM)
        return TokenVerify(**decoded_email)

    except JWTError as decode_error:
        raise ValueError("unable to decode") from decode_error
    except ValidationError as validation_error:
        raise ValueError("invalid token") from validation_error


def get_invite_from_token(token: str, secret_key: str) -> TokenInvite:
    try:
        decoded_invite = jwt.decode(token, secret_key, algorithms=ALGORITHM)
        return TokenInvite(**decoded_invite)

    except JWTError as decode_error:
        raise ValueError("unable to decode") from decode_error
    except ValidationError as validation_error:
        raise ValueError("invalid token") from validation_error


def get_website_invite_from_token(token: str, secret_key: str) -> TokenInviteWebsite:
    try:
        decoded_invite = jwt.decode(token, secret_key, algorithms=ALGORITHM)
        return TokenInviteWebsite(**decoded_invite)

    except JWTError as decode_error:
        raise ValueError("unable to decode") from decode_error
    except ValidationError as validation_error:
        raise ValueError("invalid token") from validation_error
