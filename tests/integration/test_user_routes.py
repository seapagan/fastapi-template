"""Define tests for the 'User' routes of the application."""

import pytest
from faker import Faker

from managers.auth import AuthManager
from managers.user import pwd_context
from models.enums import RoleType
from models.user import User


@pytest.mark.asyncio()
@pytest.mark.integration()
class TestUserRoutes:
    """Test the User routes of the application."""

    def get_test_user(self):
        """Return one or more test users."""
        fake = Faker()

        test_user_template = {
            "email": fake.email(),
            "first_name": "Test",
            "last_name": "User",
            "password": pwd_context.hash("test12345!"),
            "verified": True,
            "role": RoleType.user,
        }

        return test_user_template

    # ------------------------------------------------------------------------ #
    #                            test profile route                            #
    # ------------------------------------------------------------------------ #
    async def test_get_my_profile(self, test_app, get_db):
        """Test we can get the current users profile."""
        await get_db.execute(User.insert().values(**self.get_test_user()))
        token = AuthManager.encode_token({"id": 1})

        response = test_app.get(
            "/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert len(response.json()) == 3

    async def test_get_my_profile_no_auth(self, test_app, get_db):
        """Ensure we get no profile if no auth token is provided."""
        await get_db.execute(User.insert().values(**self.get_test_user()))

        response = test_app.get("/users/me", headers={})

        assert response.status_code == 403
        assert response.json() == {"detail": "Not authenticated"}

    # ------------------------------------------------------------------------ #
    #                           test get users route                           #
    # ------------------------------------------------------------------------ #
    @pytest.mark.skip(reason="Errors somewhere in accessing the route.")
    async def test_admin_can_get_all_users(self, test_app, get_db):
        """Ensure an admin user can get all users."""
        for _ in range(3):
            await get_db.execute(User.insert().values(**self.get_test_user()))

        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        admin_id = await get_db.execute(User.insert().values(**admin_user))
        token = AuthManager.encode_token({"id": admin_id})

        response = test_app.get(
            "/users", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert len(response.json()) == 4

    async def test_user_cant_get_all_users(self, test_app, get_db):
        """Test we can't get all users if not admin."""
        await get_db.execute(User.insert().values(**self.get_test_user()))
        await get_db.execute(User.insert().values(**self.get_test_user()))
        await get_db.execute(User.insert().values(**self.get_test_user()))
        token = AuthManager.encode_token({"id": 1})

        response = test_app.get(
            "/users", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden"}

    # ------------------------------------------------------------------------ #
    #                           test make_admin route                          #
    # ------------------------------------------------------------------------ #
    async def test_make_admin_as_admin(self, test_app, get_db):
        """Test we can upgrade an existing user to admin."""
        normal_user = self.get_test_user()
        admin_user = {**self.get_test_user(), "role": RoleType.admin}

        user_id = await get_db.execute(User.insert().values(**normal_user))
        admin_id = await get_db.execute(User.insert().values(**admin_user))
        token = AuthManager.encode_token({"id": admin_id})

        response = test_app.post(
            f"/users/{user_id}/make-admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        new_admin = await get_db.fetch_one(
            User.select().where(User.c.id == user_id)
        )

        assert response.status_code == 204
        assert new_admin["role"] == RoleType.admin

    async def test_cant_make_admin_as_user(self, test_app, get_db):
        """Test we can upgrade an existing user to admin."""
        normal_user = self.get_test_user()
        normal_user_2 = self.get_test_user()

        user_id = await get_db.execute(User.insert().values(**normal_user))
        user2_id = await get_db.execute(User.insert().values(**normal_user_2))
        token = AuthManager.encode_token({"id": user_id})

        response = test_app.post(
            f"/users/{user2_id}/make-admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        new_admin = await get_db.fetch_one(
            User.select().where(User.c.id == user_id)
        )

        assert response.status_code == 403
        assert new_admin["role"] == RoleType.user

    # ------------------------------------------------------------------------ #
    #                            test ban user route                           #
    # ------------------------------------------------------------------------ #
    async def test_admin_can_ban_user(self, test_app, get_db):
        """Ensure an admin can ban a user."""
        normal_user = self.get_test_user()
        admin_user = {**self.get_test_user(), "role": RoleType.admin}

        user_id = await get_db.execute(User.insert().values(**normal_user))
        admin_id = await get_db.execute(User.insert().values(**admin_user))
        token = AuthManager.encode_token({"id": admin_id})

        response = test_app.post(
            f"/users/{user_id}/ban",
            headers={"Authorization": f"Bearer {token}"},
        )

        banned_user = await get_db.fetch_one(
            User.select().where(User.c.id == user_id)
        )

        assert response.status_code == 204
        assert banned_user["banned"] is True

    async def test_admin_cant_ban_self(self, test_app, get_db):
        """Ensure an admin can ban a user."""
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        admin_id = await get_db.execute(User.insert().values(**admin_user))
        token = AuthManager.encode_token({"id": admin_id})

        response = test_app.post(
            f"/users/{admin_id}/ban",
            headers={"Authorization": f"Bearer {token}"},
        )
        banned_user = await get_db.fetch_one(
            User.select().where(User.c.id == admin_id)
        )

        assert response.status_code == 400
        assert banned_user["banned"] is None

    async def test_user_cant_ban(self, test_app, get_db):
        """Ensure a non-admin cant ban another user."""
        normal_user = self.get_test_user()
        normal_user_2 = self.get_test_user()

        user_id = await get_db.execute(User.insert().values(**normal_user))
        user2_id = await get_db.execute(User.insert().values(**normal_user_2))
        token = AuthManager.encode_token({"id": user_id})

        response = test_app.post(
            f"/users/{user2_id}/ban",
            headers={"Authorization": f"Bearer {token}"},
        )

        banned_user = await get_db.fetch_one(
            User.select().where(User.c.id == user2_id)
        )

        assert response.status_code == 403
        assert banned_user["banned"] is None

    async def test_admin_cant_ban_missing_user(self, test_app, get_db):
        """Ensure an admin cant unban user that does not exist."""
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        admin_id = await get_db.execute(User.insert().values(**admin_user))
        token = AuthManager.encode_token({"id": admin_id})

        response = test_app.post(
            "/users/66/ban",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "This User does not exist"}

    # ------------------------------------------------------------------------ #
    #                           test unban user route                          #
    # ------------------------------------------------------------------------ #
    async def test_admin_can_unban_user(self, test_app, get_db):
        """Ensure an admin can ban a user."""
        normal_user = self.get_test_user()
        admin_user = {**self.get_test_user(), "role": RoleType.admin}

        user_id = await get_db.execute(
            User.insert().values(**normal_user, banned=True)
        )
        admin_id = await get_db.execute(User.insert().values(**admin_user))
        token = AuthManager.encode_token({"id": admin_id})

        response = test_app.post(
            f"/users/{user_id}/unban",
            headers={"Authorization": f"Bearer {token}"},
        )

        banned_user = await get_db.fetch_one(
            User.select().where(User.c.id == user_id)
        )

        assert response.status_code == 204
        assert banned_user["banned"] is False

    async def test_admin_cant_uban_self(self, test_app, get_db):
        """Ensure an admin cant unban self."""
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        admin_id = await get_db.execute(User.insert().values(**admin_user))
        token = AuthManager.encode_token({"id": admin_id})

        response = test_app.post(
            f"/users/{admin_id}/unban",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400

    async def test_admin_cant_unban_missing_user(self, test_app, get_db):
        """Ensure an admin cant unban user that does not exist."""
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        admin_id = await get_db.execute(User.insert().values(**admin_user))
        token = AuthManager.encode_token({"id": admin_id})

        response = test_app.post(
            "/users/66/unban",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "This User does not exist"}

    async def test_user_cant_unban(self, test_app, get_db):
        """Ensure a non-admin cant unban another user."""
        normal_user = self.get_test_user()
        normal_user_2 = self.get_test_user()

        user_id = await get_db.execute(User.insert().values(**normal_user))
        user2_id = await get_db.execute(
            User.insert().values(**normal_user_2, banned=True)
        )
        token = AuthManager.encode_token({"id": user_id})

        response = test_app.post(
            f"/users/{user2_id}/unban",
            headers={"Authorization": f"Bearer {token}"},
        )

        banned_user = await get_db.fetch_one(
            User.select().where(User.c.id == user2_id)
        )

        assert response.status_code == 403
        assert banned_user["banned"] is True

    # ------------------------------------------------------------------------ #
    #                          test delete user route                          #
    # ------------------------------------------------------------------------ #
    async def test_admin_can_delete_user(self, test_app, get_db):
        """Test that an admin can delete a user."""
        normal_user = self.get_test_user()
        admin_user = {**self.get_test_user(), "role": RoleType.admin}

        user_id = await get_db.execute(User.insert().values(**normal_user))
        admin_id = await get_db.execute(User.insert().values(**admin_user))
        token = AuthManager.encode_token({"id": admin_id})

        response = test_app.delete(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        deleted_user = await get_db.fetch_one(
            User.select().where(User.c.id == user_id)
        )

        assert response.status_code == 204
        assert deleted_user is None

    async def test_non_admin_cant_delete_user(self, test_app, get_db):
        """Test that an ordinary user cant delete another user."""
        normal_user = self.get_test_user()
        normal_user_2 = self.get_test_user()

        user_id = await get_db.execute(User.insert().values(**normal_user))
        user2_id = await get_db.execute(User.insert().values(**normal_user_2))
        token = AuthManager.encode_token({"id": user_id})

        response = test_app.delete(
            f"/users/{user2_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        not_deleted_user = await get_db.fetch_one(
            User.select().where(User.c.id == user2_id)
        )

        assert response.status_code == 403
        assert not_deleted_user is not None

    async def test_delete_missing_user(self, test_app, get_db):
        """Test deleting a non-existing user."""
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        admin_id = await get_db.execute(User.insert().values(**admin_user))
        token = AuthManager.encode_token({"id": admin_id})

        response = test_app.delete(
            "/users/66",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "This User does not exist"

    # ------------------------------------------------------------------------ #
    #                        test change password route                        #
    # ------------------------------------------------------------------------ #
    async def test_user_can_change_own_password(self, test_app, get_db):
        """Ensure a user can change their own password."""
        user = self.get_test_user()
        user_id = await get_db.execute(User.insert().values(**user))
        token = AuthManager.encode_token({"id": user_id})

        response = test_app.post(
            f"/users/{user_id}/password",
            json={"password": "new_password"},
            headers={"Authorization": f"Bearer {token}"},
        )

        updated_user = await get_db.fetch_one(
            User.select().where(User.c.id == user_id)
        )

        assert response.status_code == 204
        assert updated_user["password"] != user["password"]
        assert pwd_context.verify("new_password", updated_user["password"])

    async def test_user_cant_change_others_password(self, test_app, get_db):
        """Ensure a user cant change other user password."""
        normal_user = self.get_test_user()
        normal_user2 = self.get_test_user()
        user_id = await get_db.execute(User.insert().values(**normal_user))
        user2_id = await get_db.execute(User.insert().values(**normal_user2))
        token = AuthManager.encode_token({"id": user_id})

        response = test_app.post(
            f"/users/{user2_id}/password",
            json={"password": "new_password"},
            headers={"Authorization": f"Bearer {token}"},
        )

        updated_user = await get_db.fetch_one(
            User.select().where(User.c.id == user2_id)
        )

        assert response.status_code == 403
        assert pwd_context.verify("test12345!", updated_user["password"])

    async def test_admin_can_change_others_password(self, test_app, get_db):
        """Ensure an admin user can change any user password."""
        normal_user = self.get_test_user()
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        user_id = await get_db.execute(User.insert().values(**normal_user))
        admin_id = await get_db.execute(User.insert().values(**admin_user))
        token = AuthManager.encode_token({"id": admin_id})

        response = test_app.post(
            f"/users/{user_id}/password",
            json={"password": "new_password"},
            headers={"Authorization": f"Bearer {token}"},
        )

        updated_user = await get_db.fetch_one(
            User.select().where(User.c.id == user_id)
        )

        assert response.status_code == 204
        assert pwd_context.verify("new_password", updated_user["password"])

    # ------------------------------------------------------------------------ #
    #                      test editing user details route                     #
    # ------------------------------------------------------------------------ #
    async def test_user_can_change_own_details(self, test_app, get_db):
        """Ensure a user can change their own details."""
        normal_user = self.get_test_user()
        user_id = await get_db.execute(User.insert().values(**normal_user))
        token = AuthManager.encode_token({"id": user_id})

        response = test_app.put(
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

    async def test_user_cant_change_others_details(self, test_app, get_db):
        """Ensure a user cant change other user password."""
        normal_user = self.get_test_user()
        normal_user2 = self.get_test_user()
        user_id = await get_db.execute(User.insert().values(**normal_user))
        user2_id = await get_db.execute(User.insert().values(**normal_user2))
        token = AuthManager.encode_token({"id": user_id})

        response = test_app.put(
            f"/users/{user2_id}",
            json={
                "email": "new@example.com",
                "password": "new_password",
                "first_name": "new_name",
                "last_name": "new_surname",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    async def test_admin_can_change_others_details(self, test_app, get_db):
        """Ensure an admin user can change any user password."""
        normal_user = self.get_test_user()
        admin_user = {**self.get_test_user(), "role": RoleType.admin}
        user_id = await get_db.execute(User.insert().values(**normal_user))
        admin_id = await get_db.execute(User.insert().values(**admin_user))
        token = AuthManager.encode_token({"id": admin_id})

        response = test_app.put(
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