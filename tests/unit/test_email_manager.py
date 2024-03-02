"""Test the EmailManager class."""

import json
from typing import TypedDict

import pytest
from fastapi import status

from app.config.settings import get_settings
from app.schemas.email import EmailSchema, EmailTemplateSchema


class EmailData(TypedDict):
    """Type definition for email data."""

    subject: str
    recipients: list[str]


@pytest.mark.unit()
class TestEmailManager:
    """Test the EmailManager class."""

    email_data: EmailData = {
        "subject": "Test Subject",
        "recipients": ["test_recipient@testing.com"],
    }

    email_schema = EmailSchema(body="Test Body", **email_data)

    email_data_with_template = EmailTemplateSchema(
        template_name="template.html", body={"name": "Test Name"}, **email_data
    )

    background_tasks_mock_path = "app.managers.email.BackgroundTasks"

    def test_init(self, email_manager) -> None:
        """Test the EmailManager constructor."""
        assert get_settings().mail_username == email_manager.conf.MAIL_USERNAME
        assert get_settings().mail_password == email_manager.conf.MAIL_PASSWORD
        assert get_settings().mail_from == email_manager.conf.MAIL_FROM
        assert email_manager.conf.SUPPRESS_SEND == 1

    @pytest.mark.asyncio()
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
