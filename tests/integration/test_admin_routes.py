"""Define tests for the admin authentication routes."""

from typing import Any

import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.helpers import hash_password
from app.models.enums import RoleType
from app.models.user import User


@pytest.mark.asyncio
@pytest.mark.integration
class TestAdminAuth:
    """Test the admin authentication routes."""

    def get_test_user(self, hashed=True, admin=False) -> dict[str, Any]:
        """Return one or more test users."""
        fake = Faker()

        return {
            "email": fake.email(),
            "first_name": "Test",
            "last_name": "User",
            "password": hash_password("test12345!") if hashed else "test12345!",
            "verified": True,
            "role": RoleType.admin if admin else RoleType.user,
        }

    async def test_admin_route_exists(self, client: AsyncClient) -> None:
        """Test that the admin route exists and redirects to the login page."""
        route = "/admin"
        response = await client.get(route, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "admin/login" in str(response.url)

    async def test_admin_routes_redirect_to_login(
        self, client: AsyncClient
    ) -> None:
        """Test that the admin routes redirect to the login if no auth."""
        routes = ["/admin/user/list", "/admin/api-key/list", "/admin/logout"]

        for route in routes:
            response = await client.get(route, follow_redirects=True)

            assert response.status_code == status.HTTP_200_OK
            assert "admin/login" in str(response.url)

    async def test_admin_login_page_exists(self, client: AsyncClient) -> None:
        """Test that the admin login pages exist.

        Logout just redirects to the login page and is tested by the library so
        we won't test.
        Were more testing to ensure the admin functionality is properly
        integrated.
        """
        route = "/admin/login"
        response = await client.get(route)

        assert response.status_code == status.HTTP_200_OK

        assert "<!DOCTYPE html>" in response.text
        assert "Username" in response.text
        assert "Password" in response.text

    async def test_admin_login_ok(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        test_sessionmaker,
        mocker,
    ) -> None:
        """Test that the admin login page works with valid credentials."""
        admin_user = User(**self.get_test_user(admin=True))
        test_db.add(admin_user)
        await test_db.commit()

        mocker.patch(
            "app.admin.auth.async_session",
            side_effect=test_sessionmaker,
        )

        route = "/admin/login"
        data = {"username": admin_user.email, "password": "test12345!"}
        response = await client.post(
            route,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_302_FOUND
        assert response.cookies.get("session") is not None

    @pytest.mark.xfail
    @pytest.mark.parametrize(
        "route",
        [
            "/admin/user/list",
            "/admin/api-key/list",
        ],
    )
    async def test_authenticated_user_access_admin_routes(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        test_sessionmaker,
        mocker,
        route,
    ) -> None:
        """Test that the admin login page works with valid credentials."""
        admin_user = User(**self.get_test_user(admin=True))
        test_db.add(admin_user)
        await test_db.commit()

        mocker.patch(
            "app.admin.auth.async_session",
            side_effect=test_sessionmaker,
        )

        # login the user first
        data = {"username": admin_user.email, "password": "test12345!"}
        response = await client.post(
            "/admin/login",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_302_FOUND
        assert response.cookies.get("session") is not None
        cookies = response.cookies

        client.cookies = cookies
        response = await client.get(route, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert route in str(response.url)

    async def test_bad_token_in_session_redirects_to_login(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        test_sessionmaker,
        mocker,
    ) -> None:
        """Test that a bad token in the session redirects to login."""
        admin_user = User(**self.get_test_user(admin=True))
        test_db.add(admin_user)
        await test_db.commit()

        mocker.patch(
            "app.admin.auth.async_session",
            side_effect=test_sessionmaker,
        )

        # login the user first
        data = {"username": admin_user.email, "password": "test12345!"}
        response = await client.post(
            "/admin/login",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_302_FOUND
        assert response.cookies.get("session") is not None
        cookies = response.cookies

        mocker.patch(
            "app.admin.auth.AdminAuth._decode_token", return_value=False
        )

        client.cookies = cookies
        response = await client.get("/admin/user/list", follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "admin/login" in str(response.url)

    async def test_downgraded_admin_redirects_to_login(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        test_sessionmaker,
        mocker,
    ) -> None:
        """Test if a valid admin is downgraded, it redirects to login."""
        admin_user = User(**self.get_test_user(admin=True))
        test_db.add(admin_user)
        await test_db.commit()

        mocker.patch(
            "app.admin.auth.async_session",
            side_effect=test_sessionmaker,
        )

        # login the user first
        data = {"username": admin_user.email, "password": "test12345!"}
        response = await client.post(
            "/admin/login",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_302_FOUND
        assert response.cookies.get("session") is not None
        cookies = response.cookies

        admin_user.role = RoleType.user
        await test_db.commit()

        client.cookies = cookies
        response = await client.get("/admin/user/list", follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "admin/login" in str(response.url)

    async def test_banned_admin_redirects_to_login(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        test_sessionmaker,
        mocker,
    ) -> None:
        """Test if a valid admin is downgraded, it redirects to login."""
        admin_user = User(**self.get_test_user(admin=True))
        test_db.add(admin_user)
        await test_db.commit()

        mocker.patch(
            "app.admin.auth.async_session",
            side_effect=test_sessionmaker,
        )

        # login the user first
        data = {"username": admin_user.email, "password": "test12345!"}
        response = await client.post(
            "/admin/login",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_302_FOUND
        assert response.cookies.get("session") is not None
        cookies = response.cookies

        admin_user.banned = True
        await test_db.commit()

        client.cookies = cookies
        response = await client.get("/admin/user/list", follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "admin/login" in str(response.url)

    async def test_non_admin_login_fails(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        test_sessionmaker,
        mocker,
    ) -> None:
        """Test that a non-admin user cannot login to the admin interface."""
        plain_user = User(**self.get_test_user())
        test_db.add(plain_user)

        await test_db.commit()

        data = {"username": plain_user.email, "password": "test12345!"}

        mocker.patch(
            "app.admin.auth.async_session",
            side_effect=test_sessionmaker,
        )

        route = "/admin/login"
        response = await client.post(
            route,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.cookies.get("session") is None

    @pytest.mark.parametrize(
        "credentials",
        [
            ("", "test123"),
            ("admin@example.com", ""),
            (42, "test123"),
            ("admin@example.com", 42),
        ],
    )
    async def test_login_bad_data(
        self,
        client: AsyncClient,
        test_db: AsyncSession,
        test_sessionmaker,
        mocker,
        credentials,
    ) -> None:
        """Test that the login route fails with bad data."""
        username, password = credentials

        admin_user = User(**self.get_test_user(admin=True))
        test_db.add(admin_user)
        await test_db.commit()

        mocker.patch(
            "app.admin.auth.async_session",
            side_effect=test_sessionmaker,
        )

        route = "/admin/login"
        data = {"username": username, "password": password}
        response = await client.post(
            route,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.cookies.get("session") is None

    async def test_logout(self, client: AsyncClient) -> None:
        """Test that the logout route works."""
        route = "/admin/logout"
        response = await client.get(route, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "admin/login" in str(response.url)
        assert response.cookies.get("token") is None

    async def test_protected_routes_redirect_to_login_if_no_auth(
        self, client: AsyncClient
    ) -> None:
        """Ensure protected routes redirect to login when not authenticated."""
        routes = [
            "/admin/user/list",
            "/admin/api-key/list",
            "/admin/logout",
        ]

        for route in routes:
            response = await client.get(route, follow_redirects=True)

            assert response.status_code == status.HTTP_200_OK
            assert "admin/login" in str(response.url)
