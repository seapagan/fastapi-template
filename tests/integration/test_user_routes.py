"""Define tests for the 'User' routes of the application."""

from typing import Any

import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.managers.auth import AuthManager
from app.managers.user import ErrorMessages, pwd_context
from app.models.enums import RoleType
from app.models.user import User


@pytest.mark.asyncio()
@pytest.mark.integration()
class TestUserRoutes:
    """Test the User routes of the application.

    This test class has a mixture of direct database access and using the API
    Classes when creating and testing Users. This is a bit messy but using
    direct access crashes some of the tests (It's due to Pydantic validation).
    This issue will be properly investigated later.
    """

    def get_test_user(self, hashed=True, admin=False) -> dict[str, Any]:
        """Return one or more test users."""
        fake = Faker()

        return {
            "email": fake.email(),
            "first_name": "Test",
            "last_name": "User",
            "password": pwd_context.hash("test12345!")
            if hashed
            else "test12345!",
            "verified": True,
            "role": RoleType.admin if admin else RoleType.user,
        }

    # ------------------------------------------------------------------------ #
    #                            test profile route                            #
    # ------------------------------------------------------------------------ #
    async def test_get_my_profile(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test we can get the current users profile."""
        test_user = User(**self.get_test_user())
        test_db.add(test_user)
        await test_db.commit()
        token = AuthManager.encode_token(test_user)

        response = await client.get(
            "/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3  # noqa: PLR2004

    async def test_get_my_profile_no_auth(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure we get no profile if no auth token is provided."""
        test_db.add(User(**self.get_test_user()))
        await test_db.commit()

        response = await client.get("/users/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Not authenticated"}

    # ------------------------------------------------------------------------ #
    #                           test get users route                           #
    # ------------------------------------------------------------------------ #
    async def test_admin_can_get_all_users(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure an admin user can get all users.

        This test will create 3 users, then create an admin user and ensure
        it can get all users.
        """
        for _ in range(3):
            test_user = User(**self.get_test_user())
            test_db.add(test_user)

        admin_user = User(**self.get_test_user(admin=True))
        test_db.add(admin_user)
        await test_db.commit()
        token = AuthManager.encode_token(admin_user)

        response = await client.get(
            "/users/", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 4  # noqa: PLR2004

    async def test_admin_can_get_one_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure an admin user can get one users."""
        for _ in range(3):
            test_user = User(**self.get_test_user())
            test_db.add(test_user)

        admin_user = User(**self.get_test_user(admin=True))
        test_db.add(admin_user)
        await test_db.commit()
        token = AuthManager.encode_token(admin_user)

        response = await client.get(
            "/users/?user_id=3", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == 3  # noqa: PLR2004

    async def test_user_cant_get_all_users(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test we can't get all users if not admin."""
        for _ in range(3):
            test_user = User(**self.get_test_user())
            test_db.add(test_user)
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        response = await client.get(
            "/users/", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Forbidden"}

    async def test_user_cant_get_single_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test we can't get all users if not admin."""
        for _ in range(3):
            test_user = User(**self.get_test_user())
            test_db.add(test_user)
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        response = await client.get(
            "/users/?user_id=2", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Forbidden"}

    # ------------------------------------------------------------------------ #
    #                           test make_admin route                          #
    # ------------------------------------------------------------------------ #
    async def test_make_admin_as_admin(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test we can upgrade an existing user to admin."""
        normal_user = self.get_test_user()
        admin_user = self.get_test_user(admin=True)

        test_db.add(User(**normal_user))
        test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=2))

        await test_db.commit()

        upgrade_user = await client.post(
            "/users/1/make-admin",
            headers={"Authorization": f"Bearer {token}"},
        )
        new_admin = await client.get(
            "/users/?user_id=1",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert upgrade_user.status_code == status.HTTP_204_NO_CONTENT
        assert new_admin.status_code == status.HTTP_200_OK
        assert new_admin.json()["role"] == RoleType.admin.value

    async def test_cant_make_admin_as_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test we can upgrade an existing user to admin."""
        normal_user = self.get_test_user()
        normal_user_2 = self.get_test_user()

        test_db.add(User(**normal_user))
        test_db.add(User(**normal_user_2))
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        upgrade_user = await client.post(
            "/users/2/make-admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        new_admin = await client.get(
            "/users/?user_id=2",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert upgrade_user.status_code == status.HTTP_403_FORBIDDEN
        assert new_admin.status_code == status.HTTP_403_FORBIDDEN

    # ------------------------------------------------------------------------ #
    #                            test ban user route                           #
    # ------------------------------------------------------------------------ #
    async def test_admin_can_ban_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure an admin can ban a user."""
        normal_user = self.get_test_user()
        admin_user = self.get_test_user(admin=True)

        test_db.add(User(**normal_user))
        test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=2))

        await test_db.commit()

        banned_response = await client.post(
            "/users/1/ban",
            headers={"Authorization": f"Bearer {token}"},
        )

        banned_user = await client.get(
            "/users/?user_id=1",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert banned_response.status_code == status.HTTP_204_NO_CONTENT
        assert banned_user.status_code == status.HTTP_200_OK
        assert banned_user.json()["banned"] is True

    async def test_admin_cant_ban_self(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure an admin can ban a user."""
        admin_user = self.get_test_user(admin=True)
        test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        response = await client.post(
            "/users/1/ban",
            headers={"Authorization": f"Bearer {token}"},
        )

        check_not_banned = await client.get(
            "/users/?user_id=1",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert check_not_banned.status_code == status.HTTP_200_OK
        assert check_not_banned.json()["banned"] is False

    async def test_user_cant_ban(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure a non-admin cant ban another user."""
        test_db.add(User(**self.get_test_user()))
        test_db.add(User(**self.get_test_user()))
        test_db.add(User(**self.get_test_user(admin=True)))
        token = AuthManager.encode_token(User(id=1))
        admin_token = AuthManager.encode_token(User(id=3))

        await test_db.commit()

        response = await client.post(
            "/users/2/ban",
            headers={"Authorization": f"Bearer {token}"},
        )

        banned_user = await client.get(
            "/users/?user_id=2",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert banned_user.status_code == status.HTTP_200_OK
        assert banned_user.json()["banned"] is False

    async def test_admin_cant_ban_missing_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure an admin cant unban user that does not exist."""
        test_db.add(User(**self.get_test_user(admin=True)))
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        response = await client.post(
            "/users/66/ban",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": ErrorMessages.USER_INVALID}

    # ------------------------------------------------------------------------ #
    #                           test unban user route                          #
    # ------------------------------------------------------------------------ #
    async def test_admin_can_unban_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure an admin can ban a user."""
        normal_user = {**self.get_test_user(), "banned": True}
        admin_user = self.get_test_user(admin=True)

        test_db.add(User(**normal_user))
        test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=2))

        await test_db.commit()

        unban_response = await client.post(
            "/users/1/unban",
            headers={"Authorization": f"Bearer {token}"},
        )
        banned_user = await client.get(
            "/users/?user_id=1",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert unban_response.status_code == status.HTTP_204_NO_CONTENT
        assert banned_user.status_code == status.HTTP_200_OK
        assert banned_user.json()["banned"] is False

    async def test_admin_cant_uban_self(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure an admin cant unban self."""
        admin_user = {**self.get_test_user(admin=True), "banned": True}
        test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        response = await client.post(
            "/users/1/unban",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_admin_cant_unban_missing_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure an admin cant unban user that does not exist."""
        test_db.add(User(**self.get_test_user(admin=True)))
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        response = await client.post(
            "/users/66/unban",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": ErrorMessages.USER_INVALID}

    async def test_user_cant_unban(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure a non-admin cant unban another user."""
        test_db.add(User(**self.get_test_user()))
        test_db.add(User(**{**self.get_test_user(), "banned": True}))
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        response = await client.post(
            "/users/2/unban",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    # ------------------------------------------------------------------------ #
    #                          test delete user route                          #
    # ------------------------------------------------------------------------ #
    async def test_admin_can_delete_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test that an admin can delete a user."""
        test_db.add(User(**self.get_test_user()))
        test_db.add(User(**self.get_test_user(admin=True)))
        token = AuthManager.encode_token(User(id=2))

        await test_db.commit()

        await client.delete(
            "/users/1",
            headers={"Authorization": f"Bearer {token}"},
        )

        response = await client.get(
            "/users/?user_id=1",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_non_admin_cant_delete_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test that an ordinary user cant delete another user."""
        test_db.add(User(**self.get_test_user()))
        test_db.add(User(**self.get_test_user()))
        test_db.add(User(**self.get_test_user(admin=True)))
        token = AuthManager.encode_token(User(id=1))
        admin_token = AuthManager.encode_token(User(id=3))

        await test_db.commit()

        response = await client.delete(
            "/users/2",
            headers={"Authorization": f"Bearer {token}"},
        )

        not_deleted_user = await client.get(
            "/users/?user_id=2",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not_deleted_user.status_code == status.HTTP_200_OK

    async def test_delete_missing_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test deleting a non-existing user."""
        test_db.add(User(**self.get_test_user(admin=True)))
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        response = await client.delete(
            "/users/66",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == ErrorMessages.USER_INVALID

    # ------------------------------------------------------------------------ #
    #                        test change password route                        #
    # ------------------------------------------------------------------------ #
    async def test_user_can_change_own_password(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure a user can change their own password."""
        user = self.get_test_user()
        test_db.add(User(**user))
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        response = await client.post(
            "/users/1/password",
            json={"password": "new_password"},
            headers={"Authorization": f"Bearer {token}"},
        )

        updated_user = await client.post(
            "/login/",
            json={"email": user["email"], "password": "new_password"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert updated_user.status_code == status.HTTP_200_OK

    async def test_user_cant_change_others_password(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure a user cant change other user password."""
        user2 = self.get_test_user()

        test_db.add(User(**self.get_test_user()))
        test_db.add(User(**user2))
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        response = await client.post(
            "/users/2/password",
            json={"password": "new_password"},
            headers={"Authorization": f"Bearer {token}"},
        )

        test_password = await client.post(
            "/login/",
            json={"email": user2["email"], "password": "test12345!"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert test_password.status_code == status.HTTP_200_OK

    async def test_admin_can_change_others_password(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure an admin user can change any user password."""
        normal_user = self.get_test_user()
        admin_user = self.get_test_user(admin=True)
        test_db.add(User(**normal_user))
        test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=2))

        await test_db.commit()

        response = await client.post(
            "/users/1/password",
            json={"password": "new_password"},
            headers={"Authorization": f"Bearer {token}"},
        )

        test_password = await client.post(
            "/login/",
            json={"email": normal_user["email"], "password": "new_password"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert test_password.status_code == status.HTTP_200_OK

    # ------------------------------------------------------------------------ #
    #                      test editing user details route                     #
    # ------------------------------------------------------------------------ #
    async def test_user_can_change_own_details(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure a user can change their own details."""
        normal_user = self.get_test_user()
        test_db.add(User(**normal_user))
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        response = await client.put(
            "/users/1",
            json={
                "email": "new@example.com",
                "password": "new_password",
                "first_name": "new_name",
                "last_name": "new_surname",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "email": "new@example.com",
            "first_name": "new_name",
            "last_name": "new_surname",
        }

    async def test_user_cant_change_others_details(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure a user cant change other user password."""
        test_db.add(User(**self.get_test_user()))
        test_db.add(User(**self.get_test_user()))
        token = AuthManager.encode_token(User(id=1))

        await test_db.commit()

        response = await client.put(
            "/users/2",
            json={
                "email": "new@example.com",
                "password": pwd_context.hash("new_password"),
                "first_name": "new_name",
                "last_name": "new_surname",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_admin_can_change_others_details(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Ensure an admin user can change any user password."""
        test_db.add(User(**self.get_test_user()))
        test_db.add(User(**self.get_test_user(admin=True)))
        token = AuthManager.encode_token(User(id=2))

        await test_db.commit()

        response = await client.put(
            "/users/1",
            json={
                "email": "new@example.com",
                "password": "new_password",
                "first_name": "new_name",
                "last_name": "new_surname",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
