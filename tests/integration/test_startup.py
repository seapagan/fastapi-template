"""Test the startup of the application.

If the database is not configured properly, the application should delete all
routes and enable the config_error route.
"""
import mock
import pytest
from databases import Database
from fastapi.testclient import TestClient

from app.config.settings import get_settings
from app.main import app


class TestStartup:
    """Test the startup of the application.

    We only test the failure case (if the database is not configured properly),
    since we already test the default success in another test.
    """

    bad_database_url = (
        "postgresql://bad_user:wrong_password@"
        "localhost:5432/"
        f"{get_settings().db_name}"
    )
    bad_db = Database(bad_database_url)

    @pytest.mark.skip(reason="Can cause issues with other tests")
    @pytest.mark.parametrize(
        "route",
        ["/", "/users", "/login", "/register"],
    )
    def test_startup_fails_no_db(self, capfd, route):
        """Test fail with bad or missing database settings.

        We test a number of routes to ensure that the error handler is working
        """
        with mock.patch("main.database", self.bad_db):
            with TestClient(app) as client:
                response = client.get(route)

                assert response.status_code == 500
                out, _ = capfd.readouterr()
                assert "ERROR" in out
                assert "Have you set up your .env file??" in out

                json_response = response.json()
                assert (
                    "ERROR: Cannot connect to the database"
                    in json_response["detail"]
                )
