from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvTypes(Enum):
    prod: str = "prod"
    dev: str = "dev"
    test: str = "test"


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    email_api_key: str
    app_env: AppEnvTypes = AppEnvTypes.dev
    email_verification_base_url: str
    smtp_host: str
    smtp_port: str
    smtp_username: str
    smtp_password: str
