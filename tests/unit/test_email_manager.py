"""Test the EmailManager class."""
import json

import pytest
from pydantic import EmailStr

from config.settings import get_settings
from managers.email import EmailManager
from schemas.email import EmailSchema, EmailTemplateSchema


@pytest.fixture(scope="module")
def manager():
    """Fixture to return an EmailManager instance.

    We disable actually sending mail by setting suppress_send to True.
    """
    return EmailManager(suppress_send=True)


class TestEmailManager:
    """Test the EmailManager class."""

    email_data = {
        "subject": "Test Subject",
        "recipients": [EmailStr("test_recipient@testing.com")],
    }

    email_schema = EmailSchema(body="Test Body", **email_data)

    email_data_with_template = EmailTemplateSchema(
        template_name="template.html", body={"name": "Test Name"}, **email_data
    )

    def test_init(self, manager):
        """Test the EmailManager constructor."""
        assert manager.conf.MAIL_USERNAME == get_settings().mail_username
        assert manager.conf.MAIL_PASSWORD == get_settings().mail_password
        assert manager.conf.MAIL_FROM == get_settings().mail_from
        assert manager.conf.SUPPRESS_SEND == 1

    @pytest.mark.asyncio()
    async def test_simple_send(self, manager):
        """Test the simple_send method."""
        response = await manager.simple_send(email_data=self.email_schema)

        assert response.status_code == 200
        assert json.loads(response.body)["message"] == "email has been sent"

    def test_background_send(self, manager, mocker):
        """Test the background_send method."""
        mock_backgroundtasks = mocker.patch("managers.email.BackgroundTasks")
        response = manager.background_send(
            mock_backgroundtasks, self.email_schema
        )
        assert response is None
        mock_backgroundtasks.add_task.assert_called_once()
        # TODO: investigate how to ensure the task is called with the correct
        # args mock_backgroundtasks.add_task.assert_called_once_with(...)

    def test_template_send(self, manager, mocker):
        """Test the template_send method."""
        mock_backgroundtasks = mocker.patch("managers.email.BackgroundTasks")
        response = manager.template_send(
            mock_backgroundtasks, self.email_data_with_template
        )
        assert response is None
        mock_backgroundtasks.add_task.assert_called_once()
        # TODO: again see if we can get more granular with the assert
