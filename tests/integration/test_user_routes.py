"""Define tests for the 'User' routes of the application."""

import pytest
from faker import Faker
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.managers.auth import AuthManager
from app.managers.user import ErrorMessages, UserManager, pwd_context
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

    mock_request_path = "app.resources.user.Request.state"

    def get_test_user(self, hashed=True):
        """Return one or more test users."""
        fake = Faker()

        test_user_template = {
            "email": fake.email(),
            "first_name": "Test",
            "last_name": "User",
            "password": pwd_context.hash("test12345!") if hashed else "test12345!",
            "verified": True,
            "role": RoleType.user,
        }

        return test_user_template

    # ------------------------------------------------------------------------ #
    #                            test profile route                            #
    # ------------------------------------------------------------------------ #
    async def test_get_my_profile(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ):
        """Test we can get the current users profile."""
        test_user = User(**self.get_test_user())

        test_db.add(test_user)
        token = AuthManager.encode_token(test_user)

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.user.id = 1

        response = await client.get(
            "/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert len(response.json()) == 3

    async def test_get_my_profile_no_auth(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ):
        """Ensure we get no profile if no auth token is provided."""
        await UserManager.register(self.get_test_user(), session=test_db)

        mock_req = mocker.patch("app.resources.user.Request.state")
        mock_req.user.id = 1

        response = await client.get("/users/me", headers={})

        assert response.status_code == 403
        assert response.json() == {"detail": "Not authenticated"}

    # ------------------------------------------------------------------------ #
    #                           test get users route                           #
    # ------------------------------------------------------------------------ #
    async def test_admin_can_get_all_users(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ):
        """Ensure an admin user can get all users.

        This test will create 3 users, then create an admin user and ensure
        it can get all users.
        """
        for _ in range(3):
            await UserManager.register(
                self.get_test_user(hashed=False), session=test_db
            )

        token, _ = await UserManager.register(
            {**self.get_test_user(hashed=False), "role": RoleType.admin},
            session=test_db,
        )

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.user.id = 4

        response = await client.get(
            "/users/", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert len(response.json()) == 4

    async def test_admin_can_get_one_user(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ):
        """Ensure an admin user can get one users."""
        for _ in range(3):
            await UserManager.register(
                self.get_test_user(hashed=False), session=test_db
            )

        token, _ = await UserManager.register(
            {**self.get_test_user(hashed=False), "role": RoleType.admin},
            session=test_db,
        )

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.user.id = 4

        response = await client.get(
            "/users/?user_id=3", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json()["id"] == 3

    async def test_user_cant_get_all_users(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ):
        """Test we can't get all users if not admin."""
        for _ in range(3):
            await UserManager.register(
                self.get_test_user(hashed=False), session=test_db
            )
        token = AuthManager.encode_token(User(id=1))

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.user.id = 1

        response = await client.get(
            "/users/", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden"}

    async def test_user_cant_get_single_user(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ):
        """Test we can't get all users if not admin."""
        for _ in range(3):
            await UserManager.register(
                self.get_test_user(hashed=False), session=test_db
            )
        token = AuthManager.encode_token(User(id=1))

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.user.id = 1

        response = await client.get(
            "/users/?user_id=2", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden"}

    # ------------------------------------------------------------------------ #
    #                           test make_admin route                          #
    # ------------------------------------------------------------------------ #
    async def test_make_admin_as_admin(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ):
        """Test we can upgrade an existing user to admin."""
        normal_user = self.get_test_user()
        admin_user = {**self.get_test_user(), "role": RoleType.admin}

        test_db.add(User(**normal_user))
        test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=2))

        print(token)

        admin_user = await test_db.get(User, 2)
        print("Admin User: ", admin_user.__dict__)

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.user = User(id=2, role=RoleType.admin)

        response = await client.post(
            "/users/1/make-admin",
            headers={"Authorization": f"Bearer {token}"},
        )
        new_admin = await test_db.get(User, 1)

        print("New Admin: ", new_admin.__dict__)

        assert response.status_code == 204
        assert new_admin is not None
        assert new_admin.role == RoleType.admin

    async def test_cant_make_admin_as_user(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """Test we can upgrade an existing user to admin."""
        normal_user = self.get_test_user()
        normal_user_2 = self.get_test_user()

        user_id = test_db.add(User(**normal_user))
        user2_id = test_db.add(User(**normal_user_2))
        token = AuthManager.encode_token(User(id=user_id))

        response = await client.post(
            f"/users/{user2_id}/make-admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        new_admin = await test_db.get(User, user_id)

        assert response.status_code == 403
        assert new_admin is not None
        assert new_admin.role == RoleType.user

    # ------------------------------------------------------------------------ #
    #                            test ban user route                           #
    # ------------------------------------------------------------------------ #
    async def test_admin_can_ban_user(self, client: AsyncClient, test_db: AsyncSession):
        """Ensure an admin can ban a user."""
        normal_user = self.get_test_user()
        admin_user = {**self.get_test_user(), "role": RoleType.admin}

        user_id = test_db.add(User(**normal_user))
        admin_id = test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=admin_id))

        response = await client.post(
            f"/users/{user_id}/ban",
            headers={"Authorization": f"Bearer {token}"},
        )

        banned_user = await test_db.get(User, user_id)

        assert response.status_code == 204
        assert banned_user is not None
        assert banned_user.banned is True

    async def test_admin_cant_ban_self(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """Ensure an admin can ban a user."""
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        admin_id = test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=admin_id))

        response = await client.post(
            f"/users/{admin_id}/ban",
            headers={"Authorization": f"Bearer {token}"},
        )
        banned_user = await test_db.get(User, admin_id)

        assert response.status_code == 400
        assert banned_user is not None
        assert banned_user.banned is None

    async def test_user_cant_ban(self, client: AsyncClient, test_db: AsyncSession):
        """Ensure a non-admin cant ban another user."""
        normal_user = self.get_test_user()
        normal_user_2 = self.get_test_user()

        user_id = test_db.add(User(**normal_user))
        user2_id = test_db.add(User(**normal_user_2))
        token = AuthManager.encode_token(User(id=user_id))

        response = await client.post(
            f"/users/{user2_id}/ban",
            headers={"Authorization": f"Bearer {token}"},
        )

        banned_user = await test_db.get(User, user2_id)

        assert response.status_code == 403
        assert banned_user is not None
        assert banned_user.banned is None

    async def test_admin_cant_ban_missing_user(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """Ensure an admin cant unban user that does not exist."""
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        admin_id = test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=admin_id))

        response = await client.post(
            "/users/66/ban",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": ErrorMessages.USER_INVALID}

    # ------------------------------------------------------------------------ #
    #                           test unban user route                          #
    # ------------------------------------------------------------------------ #
    async def test_admin_can_unban_user(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """Ensure an admin can ban a user."""
        normal_user = self.get_test_user()
        admin_user = {**self.get_test_user(), "role": RoleType.admin}

        user_id = test_db.add(User(**normal_user, banned=True))
        admin_id = test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=admin_id))

        response = await client.post(
            f"/users/{user_id}/unban",
            headers={"Authorization": f"Bearer {token}"},
        )

        banned_user = await test_db.get(User, user_id)

        assert response.status_code == 204
        assert banned_user is not None
        assert banned_user.banned is False

    async def test_admin_cant_uban_self(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """Ensure an admin cant unban self."""
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        admin_id = test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=admin_id))

        response = await client.post(
            f"/users/{admin_id}/unban",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400

    async def test_admin_cant_unban_missing_user(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """Ensure an admin cant unban user that does not exist."""
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        admin_id = test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=admin_id))

        response = await client.post(
            "/users/66/unban",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": ErrorMessages.USER_INVALID}

    async def test_user_cant_unban(self, client: AsyncClient, test_db: AsyncSession):
        """Ensure a non-admin cant unban another user."""
        normal_user = self.get_test_user()
        normal_user_2 = self.get_test_user()

        user_id = test_db.add(User(**normal_user))
        user2_id = test_db.add(User(**normal_user_2, banned=True))
        token = AuthManager.encode_token(User(id=user_id))

        response = await client.post(
            f"/users/{user2_id}/unban",
            headers={"Authorization": f"Bearer {token}"},
        )

        banned_user = await test_db.get(User, user2_id)

        assert response.status_code == 403
        assert banned_user is not None
        assert banned_user.banned is True

    # ------------------------------------------------------------------------ #
    #                          test delete user route                          #
    # ------------------------------------------------------------------------ #
    async def test_admin_can_delete_user(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ):
        """Test that an admin can delete a user."""
        normal_user = self.get_test_user()
        admin_user = {**self.get_test_user(), "role": RoleType.admin}

        test_db.add(User(**normal_user))
        test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=2))

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.user = User(id=2, role=RoleType.admin)

        await client.delete(
            "/users/1",
            headers={"Authorization": f"Bearer {token}"},
        )

        deleted_user = await test_db.get(User, 1)

        assert deleted_user is None

    async def test_non_admin_cant_delete_user(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ):
        """Test that an ordinary user cant delete another user."""
        normal_user = self.get_test_user()
        normal_user_2 = self.get_test_user()

        test_db.add(User(**normal_user))
        test_db.add(User(**normal_user_2))
        token = AuthManager.encode_token(User(id=1))

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.user = User(id=1, role=RoleType.user)

        response = await client.delete(
            "/users/2",
            headers={"Authorization": f"Bearer {token}"},
        )

        not_deleted_user = await test_db.get(User, 2)

        assert response.status_code == 403
        assert not_deleted_user is not None

    async def test_delete_missing_user(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ):
        """Test deleting a non-existing user."""
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=1))

        mock_req = mocker.patch(self.mock_request_path)
        mock_req.user = User(id=1, role=RoleType.admin)

        response = await client.delete(
            "/users/66",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == ErrorMessages.USER_INVALID

    # ------------------------------------------------------------------------ #
    #                        test change password route                        #
    # ------------------------------------------------------------------------ #
    async def test_user_can_change_own_password(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """Ensure a user can change their own password."""
        user = self.get_test_user()
        user_id = test_db.add(User(**user))
        token = AuthManager.encode_token(User(id=user_id))

        response = await client.post(
            f"/users/{user_id}/password",
            json={"password": "new_password"},
            headers={"Authorization": f"Bearer {token}"},
        )

        updated_user = await test_db.get(User, user_id)

        assert response.status_code == 204
        assert updated_user is not None
        assert updated_user.password != user["password"]
        assert pwd_context.verify("new_password", updated_user.password)

    async def test_user_cant_change_others_password(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """Ensure a user cant change other user password."""
        normal_user = self.get_test_user()
        normal_user2 = self.get_test_user()
        user_id = test_db.add(User(**normal_user))
        user2_id = test_db.add(User(**normal_user2))
        token = AuthManager.encode_token(User(id=user_id))

        response = await client.post(
            f"/users/{user2_id}/password",
            json={"password": "new_password"},
            headers={"Authorization": f"Bearer {token}"},
        )

        updated_user = await test_db.get(User, user2_id)

        assert response.status_code == 403
        assert updated_user is not None
        assert pwd_context.verify("test12345!", updated_user.password)

    async def test_admin_can_change_others_password(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """Ensure an admin user can change any user password."""
        normal_user = self.get_test_user()
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        user_id = test_db.add(User(**normal_user))
        admin_id = test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=admin_id))

        response = await client.post(
            f"/users/{user_id}/password",
            json={"password": "new_password"},
            headers={"Authorization": f"Bearer {token}"},
        )

        updated_user = await test_db.get(User, user_id)

        assert response.status_code == 204
        assert updated_user is not None
        assert pwd_context.verify("new_password", updated_user.password)

    # ------------------------------------------------------------------------ #
    #                      test editing user details route                     #
    # ------------------------------------------------------------------------ #
    async def test_user_can_change_own_details(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """Ensure a user can change their own details."""
        normal_user = self.get_test_user()
        user_id = test_db.add(User(**normal_user))
        token = AuthManager.encode_token(User(id=user_id))

        response = await client.put(
            f"/users/{user_id}",
            json={
                "email": "new@example.com",
                "password": "new_password",
                "first_name": "new_name",
                "last_name": "new_surname",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["email"] == "new@example.com"

    async def test_user_cant_change_others_details(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """Ensure a user cant change other user password."""
        normal_user = self.get_test_user()
        normal_user2 = self.get_test_user()
        user_id = test_db.add(User(**normal_user))
        user2_id = test_db.add(User(**normal_user2))
        token = AuthManager.encode_token(User(id=user_id))

        response = await client.put(
            f"/users/{user2_id}",
            json={
                "email": "new@example.com",
                "password": pwd_context.hash("new_password"),
                "first_name": "new_name",
                "last_name": "new_surname",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    async def test_admin_can_change_others_details(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """Ensure an admin user can change any user password."""
        normal_user = self.get_test_user()
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        user_id = test_db.add(User(**normal_user))
        admin_id = test_db.add(User(**admin_user))
        token = AuthManager.encode_token(User(id=admin_id))

        response = await client.put(
            f"/users/{user_id}",
            json={
                "email": "new@example.com",
                "password": "new_password",
                "first_name": "new_name",
                "last_name": "new_surname",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
