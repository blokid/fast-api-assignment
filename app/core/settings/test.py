import logging

from pydantic import PostgresDsn, SecretStr

from app.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    # fastapi_kwargs
    debug: bool = True
    title: str = "Test FastAPI example application"

    # back-end app settings
    secret_key: SecretStr = SecretStr("secret-test")
    db_url: PostgresDsn = (
        "postgresql+asyncpg://postgres:postgres@postgresql:5432/postgres"
    )
    logging_level: int = logging.DEBUG

    # front-end app settings
    frontend_url: str = "http://localhost:3000"

    # mail settings
    mail_username: str
    mail_password: SecretStr
    mail_port: int
    mail_server: str
