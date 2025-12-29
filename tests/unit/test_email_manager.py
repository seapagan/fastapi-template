"""Test the EmailManager class."""

import json
from typing import TypedDict

import pytest
from fastapi import status
from pydantic import NameEmail

from app.config.settings import get_settings
from app.schemas.email import EmailSchema, EmailTemplateSchema


class EmailData(TypedDict):
    """Type definition for email data."""

    subject: str
    recipients: list[NameEmail]


@pytest.mark.unit
class TestEmailManager:
    """Test the EmailManager class."""

    email_data: EmailData = {
        "subject": "Test Subject",
        "recipients": [
            NameEmail(name="Test Email", email="test_recipient@testing.com")
        ],
    }

    email_schema = EmailSchema(body="Test Body", **email_data)

    email_data_with_template = EmailTemplateSchema(
        template_name="template.html", body={"name": "Test Name"}, **email_data
    )

    background_tasks_mock_path = "app.managers.email.BackgroundTasks"

    def test_init(self, email_manager) -> None:
        """Test the EmailManager constructor."""
        assert get_settings().mail_username == email_manager.conf.MAIL_USERNAME
        assert (
            get_settings().mail_password
            == email_manager.conf.MAIL_PASSWORD.get_secret_value()
        )
        assert get_settings().mail_from == email_manager.conf.MAIL_FROM
        assert email_manager.conf.SUPPRESS_SEND == 1

    @pytest.mark.asyncio
    async def test_simple_send(self, email_manager) -> None:
        """Test the simple_send method."""
        response = await email_manager.simple_send(email_data=self.email_schema)

        assert response.status_code == status.HTTP_200_OK
        assert json.loads(response.body)["message"] == "email has been sent"

    def test_background_send(self, email_manager, mocker) -> None:
        """Test the background_send method."""
        mock_backgroundtasks = mocker.patch(self.background_tasks_mock_path)
        response = email_manager.background_send(
            mock_backgroundtasks, self.email_schema
        )
        assert response is None
        mock_backgroundtasks.add_task.assert_called_once()
        # TODO(seapgan): investigate how to ensure the task is called with the
        # correct args

    def test_template_send(self, email_manager, mocker) -> None:
        """Test the template_send method."""
        mock_backgroundtasks = mocker.patch(self.background_tasks_mock_path)
        response = email_manager.template_send(
            mock_backgroundtasks, self.email_data_with_template
        )
        assert response is None
        mock_backgroundtasks.add_task.assert_called_once()
        # TODO(seapgan): again see if we can get more granular with the assert

    @pytest.mark.asyncio
    async def test_simple_send_exception_handling(
        self, email_manager, mocker
    ) -> None:
        """Test simple_send logs and re-raises exceptions."""
        # COVERS: email.py lines 65-69

        # Mock FastMail to raise an exception
        mock_fastmail_class = mocker.patch("app.managers.email.FastMail")
        mock_fastmail_instance = mock_fastmail_class.return_value
        mock_fastmail_instance.send_message = mocker.AsyncMock(
            side_effect=Exception("SMTP connection failed")
        )

        # Mock category_logger to verify error logging
        mock_logger = mocker.patch("app.managers.email.category_logger.error")

        # Verify exception is raised and logged
        with pytest.raises(Exception, match="SMTP connection failed"):
            await email_manager.simple_send(email_data=self.email_schema)

        # Verify error was logged
        mock_logger.assert_called_once()
        assert "Failed to send email" in mock_logger.call_args[0][0]
