"""Test the Swagger UI routes."""
import pytest

from app.config.settings import get_settings


@pytest.mark.integration()
class TestDocRoutes:
    """Test the Swagger documentation."""

    def test_swagger_ui_html(self, test_app):
        """Test the Swagger UI docs are accessible.

        We just do very basic testing here to ensure that the docs are being
        displayed. We don't test the content of the docs themselves, except to
        ensure that the title is correct and the HTML is valid
        """
        response = test_app.get("/docs")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"

        assert response.text.strip().startswith("<!DOCTYPE html>")
        assert (
            f"<title>{get_settings().api_title} | Documentation</title>"
            in response.text
        )
