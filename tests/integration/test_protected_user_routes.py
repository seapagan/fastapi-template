"""Integration tests for user routes."""

import pytest
from fastapi import status

from app.managers.user import pwd_context


@pytest.mark.integration
class TestProtectedUserRoutes:
    """Ensure the user routes are protected by authentication.

    This is not testing the functionality of the routes, just that they are
    blocked without valid authentication.
    """

    test_user = {
        "email": "testuser@usertest.com",
        "first_name": "Test",
        "last_name": "User",
        "password": pwd_context.hash("test12345!"),
        "verified": True,
    }

    test_routes = [
        ["/users/", "get"],
        ["/users/me", "get"],
        ["/users/1/make-admin", "post"],
        ["/users/1/password", "post"],
        ["/users/1/ban", "post"],
        ["/users/1/unban", "post"],
        ["/users/1", "put"],
        ["/users/1", "delete"],
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "route",
        test_routes,
    )
    async def test_routes_no_auth(self, client, route) -> None:
        """Test that routes are protected by authentication."""
        route_name, method = route
        fn = getattr(client, method)
        response = await fn(route_name)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Not authenticated"}

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "route",
        test_routes,
    )
    async def test_routes_bad_auth(self, client, route) -> None:
        """Test that routes are protected by authentication."""
        route_name, method = route
        fn = getattr(client, method)
        response = await fn(
            route_name, headers={"Authorization": "Bearer BADBEEF"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "That token is Invalid"}
