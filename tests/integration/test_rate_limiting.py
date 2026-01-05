"""Test rate limiting functionality."""

from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest
from fastapi import status
from httpx import AsyncClient

if TYPE_CHECKING:
    from slowapi import Limiter


@pytest.fixture(autouse=True)
def reset_rate_limiter() -> Generator["Limiter", None, None]:
    """Reset rate limiter storage between tests and yield limiter instance."""
    # Import here to avoid circular imports
    from app.rate_limit import limiter  # noqa: PLC0415

    # Reset the limiter's storage before each test
    if hasattr(limiter, "_storage"):
        limiter._storage.reset()
    yield limiter
    # Clean up after test
    if hasattr(limiter, "_storage"):
        limiter._storage.reset()


@pytest.mark.integration
class TestRateLimiting:
    """Test rate limiting on authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register_rate_limit(
        self,
        client: AsyncClient,
        mocker,
        monkeypatch,
        reset_rate_limiter,
    ) -> None:
        """Ensure register endpoint enforces 3/hour limit."""
        # Enable rate limiting for this test
        monkeypatch.setattr(reset_rate_limiter, "enabled", True)

        # Mock email sending
        mocker.patch("app.managers.user.EmailManager.template_send")

        # Make 3 successful requests (within limit)
        for i in range(3):
            response = await client.post(
                "/register/",
                json={
                    "email": f"user{i}@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "password": "password123!",
                },
            )
            assert response.status_code == status.HTTP_201_CREATED

        # 4th request should be rate limited
        response = await client.post(
            "/register/",
            json={
                "email": "user4@example.com",
                "first_name": "Test",
                "last_name": "User",
                "password": "password123!",
            },
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_login_rate_limit(
        self,
        client: AsyncClient,
        test_db,
        mocker,
        monkeypatch,
        reset_rate_limiter,
    ) -> None:
        """Ensure login endpoint enforces 5/15minutes limit."""
        # Enable rate limiting for this test
        monkeypatch.setattr(reset_rate_limiter, "enabled", True)

        # Mock email sending
        mocker.patch("app.managers.user.EmailManager.template_send")

        # Make 5 login attempts (within limit)
        for _ in range(5):
            response = await client.post(
                "/login/",
                json={
                    "email": "test@example.com",
                    "password": "wrongpassword",
                },
            )
            # May fail auth (400, 401) but shouldn't be rate limited
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_200_OK,
            ]

        # 6th attempt should be rate limited
        response = await client.post(
            "/login/",
            json={
                "email": "test@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @pytest.mark.asyncio
    async def test_forgot_password_rate_limit(
        self,
        client: AsyncClient,
        mocker,
        monkeypatch,
        reset_rate_limiter,
    ) -> None:
        """Ensure forgot-password endpoint enforces 3/hour limit."""
        # Enable rate limiting for this test
        monkeypatch.setattr(reset_rate_limiter, "enabled", True)

        # Mock email sending
        mocker.patch("app.managers.email.EmailManager.template_send")

        # Make 3 requests (within limit)
        for _ in range(3):
            response = await client.post(
                "/forgot-password/",
                json={"email": "test@example.com"},
            )
            assert response.status_code == status.HTTP_200_OK

        # 4th request should be rate limited
        response = await client.post(
            "/forgot-password/",
            json={"email": "test@example.com"},
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    @pytest.mark.asyncio
    async def test_rate_limit_headers(
        self,
        client: AsyncClient,
        mocker,
        monkeypatch,
        reset_rate_limiter,
    ) -> None:
        """Ensure rate limit responses include Retry-After header."""
        # Enable rate limiting for this test
        monkeypatch.setattr(reset_rate_limiter, "enabled", True)

        mocker.patch("app.managers.user.EmailManager.template_send")

        # Exceed rate limit
        for i in range(4):
            await client.post(
                "/register/",
                json={
                    "email": f"user{i}@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "password": "password123!",
                },
            )

        response = await client.post(
            "/register/",
            json={
                "email": "user5@example.com",
                "first_name": "Test",
                "last_name": "User",
                "password": "password123!",
            },
        )

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        # slowapi should include Retry-After header
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        assert "retry-after" in headers_lower

    @pytest.mark.asyncio
    async def test_rate_limit_error_message(
        self,
        client: AsyncClient,
        mocker,
        monkeypatch,
        reset_rate_limiter,
    ) -> None:
        """Ensure rate limit error message is user-friendly."""
        # Enable rate limiting for this test
        monkeypatch.setattr(reset_rate_limiter, "enabled", True)

        mocker.patch("app.managers.user.EmailManager.template_send")

        # Exceed rate limit
        for i in range(4):
            await client.post(
                "/register/",
                json={
                    "email": f"user{i}@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "password": "password123!",
                },
            )

        response = await client.post(
            "/register/",
            json={
                "email": "user5@example.com",
                "first_name": "Test",
                "last_name": "User",
                "password": "password123!",
            },
        )

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        data = response.json()
        assert "detail" in data
        assert "rate limit" in data["detail"].lower()
