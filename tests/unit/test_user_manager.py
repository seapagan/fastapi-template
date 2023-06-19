"""Test the UserManager class."""
from typing import List

import pytest
from fastapi import BackgroundTasks, HTTPException

from app.managers.user import ErrorMessages, UserManager, pwd_context
from app.models.enums import RoleType
from app.models.user import User
from app.schemas.request.user import UserChangePasswordRequest, UserEditRequest


@pytest.mark.unit()
@pytest.mark.asyncio()
class TestUserManager:  # pylint: disable=too-many-public-methods
    """Test the UserManager class."""

    test_user = {
        "email": "testuser@usertest.com",
        "password": "test12345!",
        "first_name": "Test",
        "last_name": "User",
    }

    # ------------------------- Test register method ------------------------- #
    async def test_create_user(self, get_db):
        """Test creating a user."""
        await UserManager.register(self.test_user, get_db)
        new_user = await get_db.fetch_one(User.select().where(User.c.id == 1))

        assert new_user["email"] == self.test_user["email"]
        assert new_user["first_name"] == self.test_user["first_name"]
        assert new_user["last_name"] == self.test_user["last_name"]
        assert new_user["password"] != self.test_user["password"]

        assert pwd_context.verify(
            self.test_user["password"], new_user["password"]
        )

    async def test_create_user_with_bad_email(self, get_db):
        """Ensure you cant create a user with a bad email."""
        with pytest.raises(HTTPException, match=ErrorMessages.EMAIL_INVALID):
            await UserManager.register(
                {
                    "email": "testuser",
                    "password": "test12345!",
                    "first_name": "Test",
                    "last_name": "User",
                },
                get_db,
            )

    @pytest.mark.parametrize(
        "create_data",
        [
            {
                "email": "",
                "password": "test12345!",
                "first_name": "Test",
                "last_name": "User",
            },
            {
                "email": "testuser@usertest.com",
                "password": "",
                "first_name": "Test",
                "last_name": "User",
            },
            {
                "email": "testuser@usertest.com",
                "password": "test12345!",
                "first_name": "",
                "last_name": "User",
            },
            {
                "email": "testuser@usertest.com",
                "password": "",
                "first_name": "Test",
                "last_name": "",
            },
        ],
    )
    async def test_create_user_missing_values(self, get_db, create_data):
        """Test creating a user with missing values."""
        with pytest.raises(HTTPException, match=ErrorMessages.EMPTY_FIELDS):
            await UserManager.register(create_data, get_db)

    async def test_create_duplicate_user(self, get_db):
        """Test creating a duplicate user."""
        await UserManager.register(self.test_user, get_db)

        with pytest.raises(HTTPException, match=ErrorMessages.EMAIL_EXISTS):
            await UserManager.register(self.test_user, get_db)

    async def test_create_user_returns_tokens(self, get_db):
        """Test creating a user."""
        result = await UserManager.register(self.test_user, get_db)

        assert isinstance(result, tuple)
        assert len(result) == 2

        token, refresh = result
        assert isinstance(token, str)
        assert isinstance(refresh, str)

    async def test_register_user_verified_when_no_background_tasks_specified(
        self, get_db
    ):
        """Test user is automatically verified when no 'background_tasks'."""
        await UserManager.register(self.test_user, get_db)
        user = await get_db.fetch_one(User.select().where(User.c.id == 1))

        assert user["verified"] is True

    async def test_register_user_not_verified_when_background_tasks_specified(
        self,
        get_db,
    ):
        """Test user is not verified when 'background_tasks' IS provided."""
        background_tasks = BackgroundTasks()
        await UserManager.register(
            self.test_user, get_db, background_tasks=background_tasks
        )
        user = await get_db.fetch_one(User.select().where(User.c.id == 1))

        assert user["verified"] is False

    # --------------------------- test login method -------------------------- #
    async def test_login_user(self, get_db):
        """Test logging in a user."""
        await UserManager.register(self.test_user, get_db)
        result = await UserManager.login(self.test_user, get_db)

        assert isinstance(result, tuple)
        assert len(result) == 2

        token, refresh = result
        assert isinstance(token, str)
        assert isinstance(refresh, str)

    async def test_login_user_not_found(self, get_db):
        """Test logging in a user that doesn't exist."""
        with pytest.raises(HTTPException, match=ErrorMessages.AUTH_INVALID):
            await UserManager.login(self.test_user, get_db)

    async def test_login_user_wrong_password(self, get_db):
        """Test logging in a user with the wrong password."""
        await UserManager.register(self.test_user, get_db)
        bad_user = self.test_user.copy()
        bad_user["password"] = "wrongpassword"  # nosec
        with pytest.raises(HTTPException, match=ErrorMessages.AUTH_INVALID):
            await UserManager.login(bad_user, get_db)

    async def test_login_user_not_verified(self, get_db):
        """Test logging in a user that isn't verified.

        We can do this easily by creating a user and specify a
        'background_tasks' parameter.
        """
        background_tasks = BackgroundTasks()
        await UserManager.register(
            self.test_user, get_db, background_tasks=background_tasks
        )
        with pytest.raises(HTTPException, match=ErrorMessages.NOT_VERIFIED):
            await UserManager.login(self.test_user, get_db)

    async def test_login_user_banned(self, get_db):
        """Test logging in a user that is banned."""
        await UserManager.register(self.test_user, get_db)
        await UserManager.set_ban_status(1, True, 666, get_db)
        with pytest.raises(HTTPException, match=ErrorMessages.AUTH_INVALID):
            await UserManager.login(self.test_user, get_db)

    # -------------------------- test delete method -------------------------- #
    async def test_delete_user(self, get_db):
        """Test deleting a user."""
        await UserManager.register(self.test_user, get_db)
        await UserManager.delete_user(1, get_db)

        user = await get_db.fetch_one(User.select().where(User.c.id == 1))
        assert user is None

    async def test_delete_user_not_found(self, get_db):
        """Test deleting a user that doesn't exist."""
        with pytest.raises(HTTPException, match=ErrorMessages.USER_INVALID):
            await UserManager.delete_user(1, get_db)

    # -------------------------- test update method -------------------------- #
    async def test_update_user(self, get_db):
        """Test updating a user."""
        await UserManager.register(self.test_user, get_db)
        edited_user = self.test_user.copy()
        edited_user["first_name"] = "Edited"

        await UserManager.update_user(1, UserEditRequest(**edited_user), get_db)
        edited_user = await get_db.fetch_one(
            User.select().where(User.c.id == 1)
        )

        assert edited_user["first_name"] == "Edited"

    async def test_update_user_not_found(self, get_db):
        """Test updating a user that doesn't exist."""
        with pytest.raises(HTTPException, match=ErrorMessages.USER_INVALID):
            await UserManager.update_user(
                1, UserEditRequest(**self.test_user), get_db
            )

    # ------------------------ test changing password ------------------------ #
    async def test_change_password(self, get_db):
        """Test changing a user's password."""
        await UserManager.register(self.test_user, get_db)
        await UserManager.change_password(
            1,
            UserChangePasswordRequest(password="updated_password"),  # nosec
            get_db,
        )

        user = await get_db.fetch_one(User.select().where(User.c.id == 1))
        assert user["password"] != self.test_user["password"]

    async def test_change_password_not_found(self, get_db):
        """Test changing a user's password that doesn't exist."""
        with pytest.raises(HTTPException, match=ErrorMessages.USER_INVALID):
            await UserManager.change_password(
                1,
                UserChangePasswordRequest(password="updated_password"),  # nosec
                get_db,
            )

    # -------------------------- test set ban status ------------------------- #
    async def test_ban_user(self, get_db):
        """Test we can ban or unban a user."""
        await UserManager.register(self.test_user, get_db)
        await UserManager.set_ban_status(1, True, 666, get_db)

        banned_user = await get_db.fetch_one(
            User.select().where(User.c.id == 1)
        )
        assert banned_user["banned"] is True

    async def test_unban_user(self, get_db):
        """Test we can ban or unban a user."""
        await UserManager.register(self.test_user, get_db)
        # set this user as banned
        await UserManager.set_ban_status(1, True, 666, get_db)

        await UserManager.set_ban_status(1, False, 666, get_db)

        banned_user = await get_db.fetch_one(
            User.select().where(User.c.id == 1)
        )
        assert banned_user["banned"] is False

    async def test_ban_user_not_found(self, get_db):
        """Test we can't ban a user that doesn't exist."""
        with pytest.raises(HTTPException, match=ErrorMessages.USER_INVALID):
            await UserManager.set_ban_status(1, True, 666, get_db)

    @pytest.mark.parametrize("state", [True, False])
    async def test_cant_ban_user_already_banned(self, get_db, state):
        """Test we can't ban a user that is already banned/unbanned."""
        await UserManager.register(self.test_user, get_db)
        if state:
            await UserManager.set_ban_status(1, state, 666, get_db)

        with pytest.raises(
            HTTPException, match=ErrorMessages.ALREADY_BANNED_OR_UNBANNED
        ):
            await UserManager.set_ban_status(1, state, 666, get_db)

    async def test_cant_ban_self(self, get_db):
        """Test we can't ban ourselves."""
        await UserManager.register(self.test_user, get_db)
        with pytest.raises(HTTPException, match=ErrorMessages.CANT_SELF_BAN):
            await UserManager.set_ban_status(1, True, 1, get_db)

    # ------------------------- test change user role ------------------------ #
    async def test_change_user_role_to_admin(self, get_db):
        """Test we can change a user's role to admin."""
        await UserManager.register(self.test_user, get_db)
        await UserManager.change_role(RoleType.admin, 1, get_db)

        user_data = await get_db.fetch_one(User.select().where(User.c.id == 1))

        assert user_data["role"] == RoleType.admin

    # ----------------------- test the helper functions ---------------------- #
    async def test_get_user_by_id(self, get_db):
        """Ensure we can get a user by their id."""
        await UserManager.register(self.test_user, get_db)
        user_data = await UserManager.get_user_by_id(1, get_db)

        assert user_data is not None
        assert user_data["id"] == 1

    async def test_get_user_by_id_not_found(self, get_db):
        """Ensure we get None if the user doesn't exist."""
        user_data = await UserManager.get_user_by_id(1, get_db)

        assert user_data is None

    async def test_get_user_by_email(self, get_db):
        """Ensure we can get a user by their email."""
        await UserManager.register(self.test_user, get_db)
        user_data = await UserManager.get_user_by_email(
            self.test_user["email"], get_db
        )

        assert user_data is not None
        assert user_data["email"] == self.test_user["email"]
        assert user_data["id"] == 1

    async def test_get_user_by_email_not_found(self, get_db):
        """Ensure we get None if the user with email doesn't exist."""
        user_data = await UserManager.get_user_by_email(
            self.test_user["email"], get_db
        )

        assert user_data is None

    async def test_get_all_users(self, get_db):
        """Test getting all users."""
        user = self.test_user.copy()
        for i in range(5):
            user["email"] = f"user{i}@test.com"
            await UserManager.register(user, get_db)

        users = await UserManager.get_all_users(get_db)

        assert isinstance(users, List)
        assert len(users) == 5

    async def test_get_all_users_empty(self, get_db):
        """Test getting all users when there are none."""
        users = await UserManager.get_all_users(get_db)

        assert len(users) == 0
