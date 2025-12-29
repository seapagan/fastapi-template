"""Control the app settings, including reading from a .env file."""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path  # noqa: TC003

from cryptography.fernet import Fernet
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.helpers import get_project_root
from app.logs import logger

try:
    from .metadata import custom_metadata
except ModuleNotFoundError:  # pragma: no cover
    logger.error(
        "The metadata file could not be found, it may have been deleted."
    )
    logger.error("Please run 'api-admin custom init' to regenerate defaults.")
    sys.exit(1)

# Security validation constants
MIN_SECRET_KEY_LENGTH = 32


class Settings(BaseSettings):
    """Main Settings class.

    This allows to set some defaults, that can be overwritten from the .env
    file if it exists.

    SECURITY WARNING: Critical settings (SECRET_KEY, DB_PASSWORD, DB_USER)
    MUST be set in your .env file. The application will fail to start if
    these are not properly configured with secure values.

    Do NOT put real passwords in this file - use the .env file instead
    (it's in .gitignore and won't be stored in Git).

    To get started, copy .env.example to .env and update the values.
    """

    project_root: Path = get_project_root()

    env_file: str = str(project_root / ".env")
    model_config = SettingsConfigDict(env_file=env_file)

    base_url: str = "http://localhost:8000"
    frontend_url: str | None = None
    api_root: str = ""
    no_root_route: bool = False

    cors_origins: str = "*"

    # Setup the Postgresql database.
    # IMPORTANT: Set DB_USER and DB_PASSWORD in your .env file!
    db_user: str = "CHANGE_ME_IN_ENV_FILE"
    db_password: str = "CHANGE_ME_IN_ENV_FILE"  # noqa: S105
    db_address: str = "localhost"
    db_port: str = "5432"
    db_name: str = "api-template"

    test_with_postgres: bool = False

    # Setup the TEST Postgresql database.
    # Note: Safe defaults for local/CI testing only
    test_db_user: str = "test_user"
    test_db_password: str = "test_password_local_only"  # noqa: S105
    test_db_address: str = "localhost"
    test_db_port: str = "5432"
    test_db_name: str = "api-template-test"

    # JWT secret Key - CRITICAL SECURITY SETTING
    # Generate with: openssl rand -hex 32
    # Or Python: import secrets; secrets.token_hex(32)
    # Set SECRET_KEY in your .env file!
    secret_key: str = "CHANGE_ME_IN_ENV_FILE"  # noqa: S105
    access_token_expire_minutes: int = 120

    # Custom Metadata
    api_title: str = custom_metadata.title
    api_description: str = custom_metadata.description
    repository: str = custom_metadata.repository
    contact: dict[str, str] = custom_metadata.contact
    license_info: dict[str, str] = custom_metadata.license_info
    year: str = custom_metadata.year

    # email settings
    # Note: Set these in .env for production email functionality
    # Email features will fail gracefully if not configured
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 587
    mail_server: str = "mail.server.com"
    mail_from_name: str = "FASTAPI Template"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    mail_use_credentials: bool = True
    mail_validate_certs: bool = True

    # admin pages settings
    admin_pages_enabled: bool = False
    admin_pages_route: str = "/admin"
    admin_pages_title: str = "API Administration"
    admin_pages_encryption_key: str = Field(
        default_factory=lambda: Fernet.generate_key().decode(),
        description="Encryption key for admin session tokens",
    )
    admin_pages_timeout: int = 86400

    # Logging settings
    log_path: str = "./logs"
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_rotation: str = "1 day"  # "500 MB", "1 week", etc.
    log_retention: str = "30 days"
    log_compression: str = "zip"
    log_categories: str = (
        "ALL"  # ALL, NONE, or comma-separated: REQUESTS,AUTH,DATABASE
    )
    log_filename: str = "api.log"
    log_console_enabled: bool = False

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

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls: type[Settings], value: str) -> str:
        """Ensure secret key is not a weak or default value."""
        weak_keys = [
            "CHANGE_ME_IN_ENV_FILE",
            "32DigitsofSecretNumbers",
            "CHANGE_ME",
            "secret",
            "secretkey",
        ]
        if value.lower() in [k.lower() for k in weak_keys]:
            msg = (
                "\n"
                "=" * 70 + "\n"
                "SECURITY ERROR: SECRET_KEY is using a weak/default value!\n"
                "=" * 70 + "\n"
                "Generate a strong key with one of these commands:\n"
                "  openssl rand -hex 32\n"
                "  python -c 'import secrets; print(secrets.token_hex(32))'\n\n"
                "Then add it to your .env file:\n"
                "  SECRET_KEY=your_generated_key_here\n"
                "=" * 70
            )
            raise ValueError(msg)
        if len(value) < MIN_SECRET_KEY_LENGTH:
            msg = (
                f"SECRET_KEY must be at least {MIN_SECRET_KEY_LENGTH} "
                f"characters for security. Current length: {len(value)}"
            )
            raise ValueError(msg)
        return value

    @field_validator("db_password")
    @classmethod
    def validate_db_password(cls: type[Settings], value: str) -> str:
        """Ensure database password is not a weak or default value."""
        weak_passwords = [
            "CHANGE_ME_IN_ENV_FILE",
            "Sup3rS3cr3tP455w0rd",
            "CHANGE_ME",
            "password",
            "admin",
        ]
        if value in weak_passwords:
            msg = (
                "\n"
                "=" * 70 + "\n"
                "SECURITY ERROR: DB_PASSWORD is using a weak/default value!\n"
                "=" * 70 + "\n"
                "Set a strong database password in your .env file:\n"
                "  DB_PASSWORD=your_secure_password_here\n"
                "=" * 70
            )
            raise ValueError(msg)
        return value

    @field_validator("db_user")
    @classmethod
    def validate_db_user(cls: type[Settings], value: str) -> str:
        """Ensure database user is not a default value."""
        if value == "CHANGE_ME_IN_ENV_FILE":
            msg = (
                "\n"
                "=" * 70 + "\n"
                "CONFIGURATION ERROR: DB_USER is not set!\n"
                "=" * 70 + "\n"
                "Set your database username in your .env file:\n"
                "  DB_USER=your_database_username\n"
                "=" * 70
            )
            raise ValueError(msg)
        return value


@lru_cache
def get_settings() -> Settings:
    """Return the current settings."""
    return Settings()
