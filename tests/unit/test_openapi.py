"""Unit tests for the custom OpenAPI schema module."""

import pytest
from fastapi import FastAPI
from pytest_mock import MockerFixture

from app.config.openapi import custom_openapi


@pytest.mark.unit
class TestCustomOpenAPI:
    """Test the custom_openapi function."""

    def test_returns_cached_schema_if_exists(self) -> None:
        """Test that cached schema is returned immediately."""
        app = FastAPI()
        cached_schema = {"cached": "schema", "version": "1.0"}
        app.openapi_schema = cached_schema

        result = custom_openapi(app)

        assert result == cached_schema

    def test_generates_new_schema_if_not_cached(
        self, mocker: MockerFixture
    ) -> None:
        """Test that get_openapi is called when cache is None."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        mock_get_openapi.return_value = {"paths": {}}

        custom_openapi(app)

        mock_get_openapi.assert_called_once()

    def test_schema_is_cached_after_generation(
        self, mocker: MockerFixture
    ) -> None:
        """Test that schema is cached after first generation."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        mock_get_openapi.return_value = {"paths": {}}

        result = custom_openapi(app)

        # Verify the schema was cached
        assert app.openapi_schema == result

    def test_second_call_uses_cache(self, mocker: MockerFixture) -> None:
        """Test that get_openapi is only called once across multiple calls."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        mock_get_openapi.return_value = {"paths": {}}

        # First call
        custom_openapi(app)
        # Second call
        custom_openapi(app)

        # Verify get_openapi was only called once
        assert mock_get_openapi.call_count == 1

    def test_metrics_endpoint_tag_customization(
        self, mocker: MockerFixture
    ) -> None:
        """Test that /metrics endpoint gets Monitoring tag."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        mock_get_openapi.return_value = {
            "paths": {
                "/metrics": {"get": {"tags": ["default"], "responses": {}}}
            }
        }

        result = custom_openapi(app)

        assert result["paths"]["/metrics"]["get"]["tags"] == ["Monitoring"]

    def test_metrics_endpoint_example_added(
        self, mocker: MockerFixture
    ) -> None:
        """Test that /metrics endpoint gets example content."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        mock_get_openapi.return_value = {
            "paths": {
                "/metrics": {"get": {"tags": ["default"], "responses": {}}}
            }
        }

        result = custom_openapi(app)

        # Verify example was added
        metrics_response = result["paths"]["/metrics"]["get"]["responses"][
            "200"
        ]
        assert "content" in metrics_response
        assert "text/plain" in metrics_response["content"]
        assert "example" in metrics_response["content"]["text/plain"]
        # Verify example contains Prometheus metrics
        example = metrics_response["content"]["text/plain"]["example"]
        assert "# HELP" in example
        assert "# TYPE" in example

    def test_heartbeat_endpoint_example(self, mocker: MockerFixture) -> None:
        """Test that /heartbeat endpoint gets correct example."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        mock_get_openapi.return_value = {
            "paths": {"/heartbeat": {"get": {"responses": {}}}}
        }

        result = custom_openapi(app)

        heartbeat_response = result["paths"]["/heartbeat"]["get"]["responses"][
            "200"
        ]
        assert heartbeat_response["content"]["application/json"]["example"] == {
            "status": "ok"
        }

    def test_verify_endpoint_description(self, mocker: MockerFixture) -> None:
        """Test that /verify/ endpoint gets description."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        mock_get_openapi.return_value = {
            "paths": {"/verify/": {"get": {"responses": {}}}}
        }

        result = custom_openapi(app)

        verify_response = result["paths"]["/verify/"]["get"]["responses"]["200"]
        assert verify_response["description"] == "User successfully verified"

    def test_forgot_password_endpoint_example(
        self, mocker: MockerFixture
    ) -> None:
        """Test that /forgot-password/ endpoint gets example."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        mock_get_openapi.return_value = {
            "paths": {"/forgot-password/": {"post": {"responses": {}}}}
        }

        result = custom_openapi(app)

        forgot_response = result["paths"]["/forgot-password/"]["post"][
            "responses"
        ]["200"]
        example = forgot_response["content"]["application/json"]["example"]
        assert "message" in example
        assert "Password reset email sent" in example["message"]

    def test_reset_password_get_description(
        self, mocker: MockerFixture
    ) -> None:
        """Test that /reset-password/ GET gets correct description."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        mock_get_openapi.return_value = {
            "paths": {
                "/reset-password/": {
                    "get": {"responses": {}},
                    "post": {"responses": {}},
                }
            }
        }

        result = custom_openapi(app)

        reset_get_response = result["paths"]["/reset-password/"]["get"][
            "responses"
        ]["200"]
        assert "HTML" in reset_get_response["description"]
        assert "FRONTEND_URL" in reset_get_response["description"]

    def test_reset_password_post_example(self, mocker: MockerFixture) -> None:
        """Test that /reset-password/ POST gets example."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        mock_get_openapi.return_value = {
            "paths": {
                "/reset-password/": {
                    "get": {"responses": {}},
                    "post": {"responses": {}},
                }
            }
        }

        result = custom_openapi(app)

        reset_post_response = result["paths"]["/reset-password/"]["post"][
            "responses"
        ]["200"]
        example = reset_post_response["content"]["application/json"]["example"]
        assert example["message"] == "Password successfully reset"

    def test_missing_paths_dont_error(self, mocker: MockerFixture) -> None:
        """Test that function handles missing paths gracefully."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        # Return schema with no paths
        mock_get_openapi.return_value = {"paths": {}}

        # Should not raise an exception
        result = custom_openapi(app)

        assert result["paths"] == {}

    def test_partial_paths_handled_correctly(
        self, mocker: MockerFixture
    ) -> None:
        """Test that only present paths are modified."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        # Only include /metrics and /heartbeat
        mock_get_openapi.return_value = {
            "paths": {
                "/metrics": {"get": {"tags": ["default"], "responses": {}}},
                "/heartbeat": {"get": {"responses": {}}},
            }
        }

        result = custom_openapi(app)

        # Verify metrics and heartbeat were modified
        assert "/metrics" in result["paths"]
        assert "/heartbeat" in result["paths"]
        # Verify other paths weren't added
        assert "/verify/" not in result["paths"]
        assert "/forgot-password/" not in result["paths"]
        assert "/reset-password/" not in result["paths"]

    def test_all_endpoints_customized_together(
        self, mocker: MockerFixture
    ) -> None:
        """Test that all endpoints can be customized simultaneously."""
        app = FastAPI()
        app.openapi_schema = None

        mock_get_openapi = mocker.patch("app.config.openapi.get_openapi")
        mock_get_openapi.return_value = {
            "paths": {
                "/metrics": {"get": {"tags": ["default"], "responses": {}}},
                "/heartbeat": {"get": {"responses": {}}},
                "/verify/": {"get": {"responses": {}}},
                "/forgot-password/": {"post": {"responses": {}}},
                "/reset-password/": {
                    "get": {"responses": {}},
                    "post": {"responses": {}},
                },
            }
        }

        result = custom_openapi(app)

        # Verify all endpoints were customized
        assert result["paths"]["/metrics"]["get"]["tags"] == ["Monitoring"]
        assert "/heartbeat" in result["paths"]
        assert "/verify/" in result["paths"]
        assert "/forgot-password/" in result["paths"]
        assert "/reset-password/" in result["paths"]
