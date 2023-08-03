"""Test the EmailManager class."""
import json

import pytest
from pydantic import EmailStr

from app.config.settings import get_settings
from app.schemas.email import EmailSchema, EmailTemplateSchema


@pytest.mark.unit()
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

    background_tasks_mock_path = "app.managers.email.BackgroundTasks"

    def test_init(self, email_manager):
        """Test the EmailManager constructor."""
        assert email_manager.conf.MAIL_USERNAME == get_settings().mail_username
        assert email_manager.conf.MAIL_PASSWORD == get_settings().mail_password
        assert email_manager.conf.MAIL_FROM == get_settings().mail_from
        assert email_manager.conf.SUPPRESS_SEND == 1

    @pytest.mark.asyncio()
    async def test_simple_send(self, email_manager):
        """Test the simple_send method."""
        response = await email_manager.simple_send(email_data=self.email_schema)

        assert response.status_code == 200
        assert json.loads(response.body)["message"] == "email has been sent"

    def test_background_send(self, email_manager, mocker):
        """Test the background_send method."""
        mock_backgroundtasks = mocker.patch(self.background_tasks_mock_path)
        response = email_manager.background_send(
            mock_backgroundtasks, self.email_schema
        )
        assert response is None
        mock_backgroundtasks.add_task.assert_called_once()
        # TODO: investigate how to ensure the task is called with the correct
        # args mock_backgroundtasks.add_task.assert_called_once_with(...)

    def test_template_send(self, email_manager, mocker):
        """Test the template_send method."""
        mock_backgroundtasks = mocker.patch(self.background_tasks_mock_path)
        response = email_manager.template_send(
            mock_backgroundtasks, self.email_data_with_template
        )
        assert response is None
        mock_backgroundtasks.add_task.assert_called_once()
        # TODO: again see if we can get more granular with the assert
