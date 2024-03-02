"""Control the app settings, including reading from a .env file."""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path  # noqa: TCH003

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.helpers import get_project_root

try:
    from .metadata import custom_metadata
except ModuleNotFoundError:  # pragma: no cover
    print(
        "The metadata file could not be found, it may have been deleted.\n"
        "Please run 'api-admin custom init' to regenerate defaults."
    )
    sys.exit(1)


class Settings(BaseSettings):
    """Main Settings class.

    This allows to set some defaults, that can be overwritten from the .env
    file if it exists.
    Do NOT put passwords and similar in here, use the .env file instead, it will
    not be stored in the Git repository.
    """

    project_root: Path = get_project_root()

    env_file: str = str(project_root / ".env")
    model_config = SettingsConfigDict(env_file=env_file)

    base_url: str = "http://localhost:8000"
    api_root: str = ""
    no_root_route: bool = False

    cors_origins: str = "*"

    # Setup the Postgresql database.
    db_user: str = "my_db_username"
    db_password: str = "Sup3rS3cr3tP455w0rd"  # nosec
    db_address: str = "localhost"
    db_port: str = "5432"
    db_name: str = "api-template"

    test_with_postgres: bool = False

    # Setup the TEST Postgresql database.
    test_db_user: str = "my_db_username"
    test_db_password: str = "Sup3rS3cr3tP455w0rd"  # nosec
    test_db_address: str = "localhost"
    test_db_port: str = "5432"
    test_db_name: str = "api-template-test"

    # JTW secret Key
    secret_key: str = "32DigitsofSecretNumbers"  # nosec
    access_token_expire_minutes: int = 120

    # Custom Metadata
    api_title: str = custom_metadata.title
    api_description: str = custom_metadata.description
    repository: str = custom_metadata.repository
    contact: dict[str, str] = custom_metadata.contact
    license_info: dict[str, str] = custom_metadata.license_info
    year: str = custom_metadata.year

    # email settings
    mail_username: str = "test_username"
    mail_password: str = "s3cr3tma1lp@ssw0rd"  # nosec
    mail_from: str = "test@email.com"
    mail_port: int = 587
    mail_server: str = "mail.server.com"
    mail_from_name: str = "FASTAPI Template"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    mail_use_credentials: bool = True
    mail_validate_certs: bool = True

    # gatekeeper settings!
    # this is to ensure that people read the damn instructions and changelogs
    i_read_the_damn_docs: bool = False

    @field_validator("api_root")
    @classmethod
    def check_api_root(cls: type[Settings], value: str) -> str:
        """Ensure the api_root does not end with a slash."""
        if value and value.endswith("/"):
            return value[:-1]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return the current settings."""
    return Settings()
