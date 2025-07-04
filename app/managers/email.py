"""Define the Email Manager."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional

from fastapi import BackgroundTasks  # noqa: TC002
from fastapi.responses import JSONResponse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import SecretStr

from app.config.settings import get_settings

if TYPE_CHECKING:  # pragma: no cover
    from app.schemas.email import EmailSchema, EmailTemplateSchema


class EmailManager:
    """Class to manage all Email operations."""

    def __init__(self, *, suppress_send: Optional[bool] = False) -> None:
        """Initialize the EmailManager.

        Define the configuration instance.
        """
        self.conf = ConnectionConfig(
            MAIL_USERNAME=get_settings().mail_username,
            MAIL_PASSWORD=SecretStr(get_settings().mail_password),
            MAIL_FROM=get_settings().mail_from,
            MAIL_PORT=get_settings().mail_port,
            MAIL_SERVER=get_settings().mail_server,
            MAIL_FROM_NAME=get_settings().mail_from_name,
            MAIL_STARTTLS=get_settings().mail_starttls,
            MAIL_SSL_TLS=get_settings().mail_ssl_tls,
            USE_CREDENTIALS=get_settings().mail_use_credentials,
            VALIDATE_CERTS=get_settings().mail_validate_certs,
            TEMPLATE_FOLDER=Path(__file__).parent / ".." / "templates/email",
            SUPPRESS_SEND=1 if suppress_send else 0,
        )

    async def simple_send(self, email_data: EmailSchema) -> JSONResponse:
        """Send a plain email with a subject and message."""
        message = MessageSchema(
            subject=email_data.subject,
            recipients=email_data.recipients,
            body=email_data.body,
            subtype=MessageType.html,
        )

        fm = FastMail(self.conf)
        await fm.send_message(message)
        return JSONResponse(
            status_code=200, content={"message": "email has been sent"}
        )

    def background_send(
        self, backgroundtasks: BackgroundTasks, email_data: EmailSchema
    ) -> None:
        """Send an email in the background."""
        message = MessageSchema(
            subject=email_data.subject,
            recipients=email_data.recipients,
            body=email_data.body,
            subtype=MessageType.html,
        )

        fm = FastMail(self.conf)
        backgroundtasks.add_task(fm.send_message, message)

    def template_send(
        self, backgroundtasks: BackgroundTasks, email_data: EmailTemplateSchema
    ) -> None:
        """Send an email using a Jinja Template."""
        message = MessageSchema(
            subject=email_data.subject,
            recipients=email_data.recipients,
            subtype=MessageType.html,
            template_body=email_data.body,
        )
        fm = FastMail(self.conf)
        backgroundtasks.add_task(
            fm.send_message, message, template_name=email_data.template_name
        )
