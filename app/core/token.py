from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from pydantic import ValidationError

from app.models.user import User
from app.schemas.token import TokenBase, TokenUser
from app.schemas.user import UserTokenData

TOKEN_TYPE = "bearer"
JWT_SUBJECT = "access"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
EMAIL_VERIFICATION_SUBJECT = "email_verification"


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
        id=user.id, username=user.username, email=user.email).model_dump()
    created_token = create_token(
        content=token_user_dict,
        secret_key=secret_key,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return UserTokenData(access_token=created_token, token_type=TOKEN_TYPE)


def get_user_from_token(token: str, secret_key: str) -> str:
    try:
        decoded_user = jwt.decode(token, secret_key, algorithms=ALGORITHM)
        return TokenUser(**decoded_user)

    except JWTError as decode_error:
        raise ValueError("unable to decode") from decode_error
    except ValidationError as validation_error:
        raise ValueError("invalid token") from validation_error


def create_email_verification_token(email: str, secret_key: str) -> str:
    to_encode = {
        "email": email,
        "sub": EMAIL_VERIFICATION_SUBJECT,
    }

    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)


def verify_email_verification_token(token: str, secret_key: str) -> str:
    try:
        decoded = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        if decoded.get("sub") != EMAIL_VERIFICATION_SUBJECT:
            raise ValueError("Invalid token subject")
        return decoded.get("email")

    except JWTError as decode_error:
        raise ValueError("Invalid token") from decode_error
    except ValidationError as validation_error:
        raise ValueError("Token validation failed") from validation_error
