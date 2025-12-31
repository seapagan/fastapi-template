"""Custom OpenAPI schema configuration."""

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI) -> dict[str, Any]:
    """Customize OpenAPI schema for special endpoints.

    Sets proper tags and examples for endpoints that can't be configured
    through standard FastAPI route decorators (e.g., third-party libraries).
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Set proper tag and example for /metrics endpoint
    if "/metrics" in openapi_schema["paths"]:
        openapi_schema["paths"]["/metrics"]["get"]["tags"] = ["Monitoring"]
        # fmt: off
        metrics_example = (
            "# HELP fastapi_template_http_requests_total "
            "Total HTTP requests\n"
            "# TYPE fastapi_template_http_requests_total counter\n"
            'fastapi_template_http_requests_total{method="GET",'
            'path="/heartbeat",status="200"} 42.0\n'
            'fastapi_template_http_requests_total{method="POST",'
            'path="/login/",status="200"} 15.0\n'
            "# HELP fastapi_template_http_request_duration_seconds "
            "HTTP request latency\n"
            "# TYPE fastapi_template_http_request_duration_seconds "
            "histogram\n"
            'fastapi_template_http_request_duration_seconds_bucket{'
            'le="0.01",method="GET",path="/heartbeat"} 40.0\n'
            'fastapi_template_http_request_duration_seconds_bucket{'
            'le="0.05",method="GET",path="/heartbeat"} 42.0\n'
            'fastapi_template_http_request_duration_seconds_bucket{'
            'le="+Inf",method="GET",path="/heartbeat"} 42.0\n'
            'fastapi_template_http_request_duration_seconds_sum{'
            'method="GET",path="/heartbeat"} 0.328\n'
            'fastapi_template_http_request_duration_seconds_count{'
            'method="GET",path="/heartbeat"} 42.0\n'
            "# HELP fastapi_template_http_requests_in_progress "
            "HTTP requests currently being processed\n"
            "# TYPE fastapi_template_http_requests_in_progress gauge\n"
            "fastapi_template_http_requests_in_progress 2.0\n"
            "# HELP fastapi_template_auth_failures_total "
            "Failed authentication attempts\n"
            "# TYPE fastapi_template_auth_failures_total counter\n"
            'fastapi_template_auth_failures_total{method="invalid_token"}'
            " 3.0\n"
            "# HELP fastapi_template_login_attempts_total "
            "Login attempts\n"
            "# TYPE fastapi_template_login_attempts_total counter\n"
            'fastapi_template_login_attempts_total{status="success"} 15.0\n'
            'fastapi_template_login_attempts_total{status="failure"} 2.0'
        )
        # fmt: on
        openapi_schema["paths"]["/metrics"]["get"]["responses"]["200"] = {
            "description": "Prometheus metrics in text format",
            "content": {"text/plain": {"example": metrics_example}},
        }

    # Add example for /heartbeat endpoint
    if "/heartbeat" in openapi_schema["paths"]:
        openapi_schema["paths"]["/heartbeat"]["get"]["responses"]["200"] = {
            "description": "Service is healthy",
            "content": {"application/json": {"example": {"status": "ok"}}},
        }

    # Add example for /verify/ endpoint
    if "/verify/" in openapi_schema["paths"]:
        openapi_schema["paths"]["/verify/"]["get"]["responses"]["200"] = {
            "description": "User successfully verified"
        }

    # Add example for /forgot-password/ endpoint
    if "/forgot-password/" in openapi_schema["paths"]:
        openapi_schema["paths"]["/forgot-password/"]["post"]["responses"][
            "200"
        ] = {
            "description": "Password reset email sent",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Password reset email sent if user exists"
                    }
                }
            },
        }

    # Add examples for /reset-password/ endpoints
    if "/reset-password/" in openapi_schema["paths"]:
        # GET returns HTML form or redirects to frontend
        openapi_schema["paths"]["/reset-password/"]["get"]["responses"][
            "200"
        ] = {
            "description": (
                "Password reset form (HTML) or redirect to frontend if "
                "FRONTEND_URL is configured"
            )
        }

        # POST returns success message for JSON API
        openapi_schema["paths"]["/reset-password/"]["post"]["responses"][
            "200"
        ] = {
            "description": "Password successfully reset",
            "content": {
                "application/json": {
                    "example": {"message": "Password successfully reset"}
                }
            },
        }

    app.openapi_schema = openapi_schema
    return app.openapi_schema
