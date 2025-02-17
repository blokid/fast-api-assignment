import logging

from pydantic import PostgresDsn, SecretStr

from app.core.settings.app import AppSettings


class ProdAppSettings(AppSettings):
    # fastapi_kwargs
    debug: bool = False
    title: str = "Production FastAPI example application"

    # back-end app settings
    secret_key: SecretStr = SecretStr("secret-prod")
    db_url: PostgresDsn = (
        "postgresql+asyncpg://postgres:postgres@postgresql:5432/postgres"
    )
    logging_level: int = logging.INFO

    # front-end app settings
    frontend_url: str = "https://example.com"

    # mail settings
    mail_username: str
    mail_password: SecretStr
    mail_port: int
    mail_server: str
