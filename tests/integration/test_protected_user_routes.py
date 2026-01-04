"""Integration tests for user routes."""

import datetime

import jwt
import pytest
from fastapi import status

from app.config.settings import get_settings
from app.database.helpers import hash_password
from app.managers.auth import AuthManager
from app.models.user import User


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
        "password": hash_password("test12345!"),
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

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": "Not authenticated. Use either JWT token or API key."
        }

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

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "route",
        test_routes,
    )
    async def test_routes_refresh_token_rejected(
        self, client, test_db, route
    ) -> None:
        """Test that refresh tokens are rejected on protected routes."""
        test_user = User(**self.test_user)
        test_db.add(test_user)
        await test_db.commit()
        refresh_token = AuthManager.encode_refresh_token(test_user)

        route_name, method = route
        fn = getattr(client, method)
        response = await fn(
            route_name, headers={"Authorization": f"Bearer {refresh_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "That token is Invalid"}

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "route",
        test_routes,
    )
    async def test_routes_missing_typ_rejected(
        self, client, test_db, route
    ) -> None:
        """Test that tokens without typ are rejected on protected routes."""
        test_user = User(**self.test_user)
        test_db.add(test_user)
        await test_db.commit()
        token = jwt.encode(
            {
                "sub": test_user.id,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(minutes=10),
            },
            get_settings().secret_key,
            algorithm="HS256",
        )

        route_name, method = route
        fn = getattr(client, method)
        response = await fn(
            route_name, headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "That token is Invalid"}
