"""Control the app settings, including reading from a .env file."""
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Main Settings class.

    This allows to set some defaults, that will be overwritten from the .env
    file if it exists.
    """

    base_url: str = "http://localhost:8000"

    cors_origins: str = "*"

    # Setup the Postgresql database.
    db_user = "my_db_username"
    db_password = "Sup3rS3cr3tP455w0rd"
    db_address = "localhost"
    db_port = "5432"
    db_name = "api-template"

    secret_key = "32DigitsofSecretNembers"

    class Config:
        """Override the default variables from an .env file, if it exsits."""

        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """Return the current settings."""
    return Settings()
