"""Integration tests for cache functionality.

Tests middleware integration.
"""

import pytest
from fastapi import status

from app.database.helpers import hash_password
from app.managers.auth import AuthManager
from app.models.enums import RoleType
from app.models.user import User


@pytest.mark.integration
class TestCacheMiddleware:
    """Test cache logging middleware integration."""

    @pytest.mark.asyncio
    async def test_middleware_handles_cache_control_header(
        self, client
    ) -> None:
        """Test middleware processes requests with Cache-Control header.

        This covers line 26 in cache_logging.py where the middleware
        checks for and logs the Cache-Control header. We can't easily
        verify loguru output, but we can verify the code path executes.
        """
        # Request with Cache-Control header (triggers line 26)
        response = await client.get(
            "/",
            headers={"Cache-Control": "no-cache"},
        )
        assert response.status_code == status.HTTP_200_OK

        # Middleware processed the request without error (coverage achieved)

    @pytest.mark.asyncio
    async def test_middleware_logs_cache_hit(self, client, test_db) -> None:
        """Ensure cache hit branch executes when response is cached."""
        admin_user = User(
            email="admin@test.com",
            first_name="Admin",
            last_name="User",
            password=hash_password("test12345!"),
            verified=True,
            role=RoleType.admin,
        )
        test_db.add(admin_user)
        await test_db.flush()
        admin_user_id = admin_user.id
        await test_db.commit()

        token = AuthManager.encode_token(User(id=admin_user_id))

        response = await client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK

        response = await client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.headers.get("X-FastAPI-Cache") == "HIT"
