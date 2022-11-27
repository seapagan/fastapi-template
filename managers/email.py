"""Define the Email Manager."""
from fastapi.responses import JSONResponse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from config.settings import get_settings


class EmailManager:
    """Class to manage all Email operations."""

    def __init__(self):
        """Initialize the EmailManager.

        Define the configuration instance.
        """
        self.conf = ConnectionConfig(
            MAIL_USERNAME=get_settings().mail_username,
            MAIL_PASSWORD=get_settings().mail_password,
            MAIL_FROM=EmailStr(get_settings().mail_from),
            MAIL_PORT=get_settings().mail_ssl_tls,
            MAIL_SERVER=get_settings().mail_server,
            MAIL_FROM_NAME=get_settings().mail_from_name,
            MAIL_STARTTLS=get_settings().mail_starttls,
            MAIL_SSL_TLS=get_settings().mail_ssl_tls,
            USE_CREDENTIALS=get_settings().mail_use_credentials,
            VALIDATE_CERTS=get_settings().mail_validate_certs,
        )

    async def simple_send(self, email_to, subject: str, msg: str):
        """Send a plain email with a subject and message."""
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=msg,
            subtype=MessageType.html,
        )

        fm = FastMail(self.conf)
        await fm.send_message(message)
        return JSONResponse(
            status_code=200, content={"message": "email has been sent"}
        )
