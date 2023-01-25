"""Control the app settings, including reading from a .env file."""
from functools import lru_cache

from pydantic import BaseSettings

try:
    from .metadata import custom_metadata
except ModuleNotFoundError:
    print(
        "The metadata file could not be found, it may have been deleted.\n"
        "Please run 'api-admin custom init' to regenerate defaults."
    )
    quit(1)


class Settings(BaseSettings):
    """Main Settings class.

    This allows to set some defaults, that can be overwritten from the .env
    file if it exists.
    Do NOT put passwords and similar in here, use the .env file instead, it will
    not be stored in the Git repository.
    """

    base_url: str = "http://localhost:8000"

    cors_origins: str = "*"

    # Setup the Postgresql database.
    db_user = "my_db_username"
    db_password = "Sup3rS3cr3tP455w0rd"
    db_address = "localhost"
    db_port = "5432"
    db_name = "api-template"

    # JTW secret Key
    secret_key = "32DigitsofSecretNembers"

    # Custom Metadata
    api_title = custom_metadata.title
    api_description = custom_metadata.description
    repository = custom_metadata.repository
    contact = custom_metadata.contact
    license_info = custom_metadata.license_info
    year = custom_metadata.year

    # email settings
    mail_username = "test_username"
    mail_password = "s3cr3tma1lp@ssw0rd"
    mail_from = "test@email.com"
    mail_port = 587
    mail_server = "mail.server.com"
    mail_from_name = "FASTAPI Template"
    mail_starttls = True
    mail_ssl_tls = False
    mail_use_credentials = True
    mail_validate_certs = True

    class Config:
        """Override the default variables from an .env file, if it exsits."""

        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """Return the current settings."""
    return Settings()
