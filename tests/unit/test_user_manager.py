"""Test the UserManager class."""

import pytest
from fastapi import BackgroundTasks, HTTPException, status

from app.database.helpers import verify_password
from app.managers.user import ErrorMessages, UserManager
from app.models.enums import RoleType
from app.models.user import User
from app.schemas.request.user import (
    SearchField,
    UserChangePasswordRequest,
    UserEditRequest,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestUserManager:  # pylint: disable=too-many-public-methods
    """Test the UserManager class."""

    test_user = {
        "email": "testuser@usertest.com",
        "password": "test12345!",
        "first_name": "Test",
        "last_name": "User",
    }

    # ------------------------- Test register method ------------------------- #
    async def test_create_user(self, test_db) -> None:
        """Test creating a user."""
        await UserManager.register(self.test_user, test_db)
        new_user = await test_db.get(User, 1)

        assert new_user.email == self.test_user["email"]
        assert new_user.first_name == self.test_user["first_name"]
        assert new_user.last_name == self.test_user["last_name"]
        assert new_user.password != self.test_user["password"]

        assert verify_password(self.test_user["password"], new_user.password)

    async def test_create_user_with_bad_email(self, test_db) -> None:
        """Ensure you cant create a user with a bad email."""
        with pytest.raises(HTTPException, match=ErrorMessages.EMAIL_INVALID):
            await UserManager.register(
                {
                    "email": "testuser",
                    "password": "test12345!",
                    "first_name": "Test",
                    "last_name": "User",
                },
                test_db,
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
    async def test_create_user_missing_values(
        self, test_db, create_data
    ) -> None:
        """Test creating a user with missing values."""
        # If password is empty, we should get PASSWORD_INVALID error
        if "password" in create_data and not create_data["password"]:
            with pytest.raises(HTTPException) as exc_info:
                await UserManager.register(create_data, test_db)
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == ErrorMessages.PASSWORD_INVALID
        else:
            # For other empty fields, we should get EMPTY_FIELDS error
            with pytest.raises(HTTPException) as exc_info:
                await UserManager.register(create_data, test_db)
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == ErrorMessages.EMPTY_FIELDS

    async def test_create_duplicate_user(self, test_db) -> None:
        """Test creating a duplicate user."""
        await UserManager.register(self.test_user, test_db)

        with pytest.raises(HTTPException, match=ErrorMessages.EMAIL_EXISTS):
            await UserManager.register(self.test_user, test_db)

    async def test_create_user_returns_tokens(self, test_db) -> None:
        """Test creating a user."""
        result = await UserManager.register(self.test_user, test_db)

        assert isinstance(result, tuple)
        assert len(result) == 2  # noqa: PLR2004

        token, refresh = result
        assert isinstance(token, str)
        assert isinstance(refresh, str)

    async def test_register_user_verified_when_no_background_tasks_specified(
        self, test_db
    ) -> None:
        """Test user is automatically verified when no 'background_tasks'."""
        await UserManager.register(self.test_user, test_db)
        user = await test_db.get(User, 1)

        assert user.verified is True

    async def test_register_user_not_verified_when_background_tasks_specified(
        self,
        test_db,
    ) -> None:
        """Test user is not verified when 'background_tasks' IS provided."""
        background_tasks = BackgroundTasks()
        await UserManager.register(
            self.test_user, test_db, background_tasks=background_tasks
        )
        user = await test_db.get(User, 1)

        assert user.verified is False

    # --------------------------- test login method -------------------------- #
    async def test_login_user(self, test_db) -> None:
        """Test logging in a user."""
        await UserManager.register(self.test_user, test_db)
        result = await UserManager.login(self.test_user, test_db)

        assert isinstance(result, tuple)
        assert len(result) == 2  # noqa: PLR2004

        token, refresh = result
        assert isinstance(token, str)
        assert isinstance(refresh, str)

    async def test_login_user_not_found(self, test_db) -> None:
        """Test logging in a user that doesn't exist."""
        with pytest.raises(HTTPException, match=ErrorMessages.AUTH_INVALID):
            await UserManager.login(self.test_user, test_db)

    async def test_login_user_wrong_password(self, test_db) -> None:
        """Test logging in a user with the wrong password."""
        await UserManager.register(self.test_user, test_db)
        bad_user = self.test_user.copy()
        bad_user["password"] = "wrongpassword"  # noqa: S105
        with pytest.raises(HTTPException, match=ErrorMessages.AUTH_INVALID):
            await UserManager.login(bad_user, test_db)

    async def test_login_user_not_verified(self, test_db) -> None:
        """Test logging in a user that isn't verified.

        We can do this easily by creating a user and specify a
        'background_tasks' parameter.
        """
        background_tasks = BackgroundTasks()
        await UserManager.register(
            self.test_user, test_db, background_tasks=background_tasks
        )
        with pytest.raises(HTTPException, match=ErrorMessages.NOT_VERIFIED):
            await UserManager.login(self.test_user, test_db)

    async def test_login_user_banned(self, test_db) -> None:
        """Test logging in a user that is banned."""
        await UserManager.register(self.test_user, test_db)
        await UserManager.set_ban_status(1, True, 666, test_db)
        with pytest.raises(HTTPException, match=ErrorMessages.AUTH_INVALID):
            await UserManager.login(self.test_user, test_db)

    # -------------------------- test delete method -------------------------- #
    async def test_delete_user(self, test_db) -> None:
        """Test deleting a user."""
        await UserManager.register(self.test_user, test_db)
        await UserManager.delete_user(1, test_db)

        user = await test_db.get(User, 1)
        assert user is None

    async def test_delete_user_not_found(self, test_db) -> None:
        """Test deleting a user that doesn't exist."""
        with pytest.raises(HTTPException, match=ErrorMessages.USER_INVALID):
            await UserManager.delete_user(1, test_db)

    # -------------------------- test update method -------------------------- #
    async def test_update_user(self, test_db) -> None:
        """Test updating a user."""
        await UserManager.register(self.test_user, test_db)
        edited_user = self.test_user.copy()
        edited_user["first_name"] = "Edited"

        updated_user = await UserManager.update_user(
            1, UserEditRequest(**edited_user), test_db
        )
        assert updated_user is not None
        assert updated_user.first_name == "Edited"

    async def test_update_user_not_found(self, test_db) -> None:
        """Test updating a user that doesn't exist."""
        with pytest.raises(HTTPException, match=ErrorMessages.USER_INVALID):
            await UserManager.update_user(
                1, UserEditRequest(**self.test_user), test_db
            )

    async def test_update_user_not_found_raises_correct_error(
        self, test_db
    ) -> None:
        """Test that updating a non-existent user raises USER_INVALID."""
        non_existent_id = 999
        user_data = UserEditRequest(
            email="new@email.com",
            first_name="New",
            last_name="Name",
            password="newpassword123!",  # noqa: S106
        )

        # Ensure we go through the actual UserManager.get_user_by_id method
        with pytest.raises(HTTPException) as exc_info:
            await UserManager.update_user(non_existent_id, user_data, test_db)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorMessages.USER_INVALID

    async def test_update_user_with_invalid_password_format(
        self, test_db, mocker
    ) -> None:
        """Test updating a user with an invalid password format raises error."""
        # First create a user
        await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )

        # Mock hash_password to raise ValueError
        mocker.patch(
            "app.managers.user.hash_password",
            side_effect=ValueError("Invalid password"),
        )

        user_data = UserEditRequest(
            email=self.test_user["email"],
            first_name=self.test_user["first_name"],
            last_name=self.test_user["last_name"],
            password="invalid",  # noqa: S106
        )

        with pytest.raises(HTTPException) as exc_info:
            await UserManager.update_user(user.id, user_data, test_db)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == ErrorMessages.PASSWORD_INVALID

    # ------------------------ test changing password ------------------------ #
    async def test_change_password(self, test_db) -> None:
        """Test changing a user's password."""
        await UserManager.register(self.test_user, test_db)
        await UserManager.change_password(
            1,
            UserChangePasswordRequest(password="updated_password"),  # noqa: S106
            test_db,
        )

        user = await test_db.get(User, 1)
        assert user.password != self.test_user["password"]

    async def test_change_password_not_found(self, test_db) -> None:
        """Test changing a user's password that doesn't exist."""
        with pytest.raises(HTTPException, match=ErrorMessages.USER_INVALID):
            await UserManager.change_password(
                1,
                UserChangePasswordRequest(password="updated_password"),  # noqa: S106
                test_db,
            )

    # -------------------------- test set ban status ------------------------- #
    async def test_ban_user(self, test_db) -> None:
        """Test we can ban or unban a user."""
        await UserManager.register(self.test_user, test_db)
        await UserManager.set_ban_status(1, True, 666, test_db)

        banned_user = await test_db.get(User, 1)
        assert banned_user.banned is True

    async def test_unban_user(self, test_db) -> None:
        """Test we can ban or unban a user."""
        await UserManager.register(self.test_user, test_db)
        # set this user as banned
        await UserManager.set_ban_status(1, True, 666, test_db)

        await UserManager.set_ban_status(1, False, 666, test_db)

        banned_user = await test_db.get(User, 1)
        assert banned_user.banned is False

    async def test_ban_user_not_found(self, test_db) -> None:
        """Test we can't ban a user that doesn't exist."""
        with pytest.raises(HTTPException, match=ErrorMessages.USER_INVALID):
            await UserManager.set_ban_status(1, True, 666, test_db)

    @pytest.mark.parametrize("state", [True, False])
    async def test_cant_ban_user_already_banned(self, test_db, state) -> None:
        """Test we can't ban a user that is already banned/unbanned."""
        await UserManager.register(self.test_user, test_db)
        if state:
            await UserManager.set_ban_status(1, state, 666, test_db)

        with pytest.raises(
            HTTPException, match=ErrorMessages.ALREADY_BANNED_OR_UNBANNED
        ):
            await UserManager.set_ban_status(1, state, 666, test_db)

    async def test_cant_ban_self(self, test_db) -> None:
        """Test we can't ban ourselves."""
        await UserManager.register(self.test_user, test_db)
        with pytest.raises(HTTPException, match=ErrorMessages.CANT_SELF_BAN):
            await UserManager.set_ban_status(1, True, 1, test_db)

    # ------------------------- test change user role ------------------------ #
    async def test_change_user_role_to_admin(self, test_db) -> None:
        """Test we can change a user's role to admin."""
        await UserManager.register(self.test_user, test_db)
        await UserManager.change_role(RoleType.admin, 1, test_db)

        user_data = await test_db.get(User, 1)

        assert user_data.role == RoleType.admin

    # ----------------------- test the helper functions ---------------------- #
    async def test_get_user_by_id(self, test_db) -> None:
        """Ensure we can get a user by their id."""
        await UserManager.register(self.test_user, test_db)
        user_data = await UserManager.get_user_by_id(1, test_db)

        assert user_data is not None
        assert user_data.id == 1

    async def test_get_user_by_id_not_found(self, test_db) -> None:
        """Ensure we get None if the user doesn't exist."""
        with pytest.raises(HTTPException, match=ErrorMessages.USER_INVALID):
            await UserManager.get_user_by_id(1, test_db)

    async def test_get_user_by_email(self, test_db) -> None:
        """Ensure we can get a user by their email."""
        await UserManager.register(self.test_user, test_db)

        user_data = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )

        assert user_data is not None
        assert user_data.email == self.test_user["email"]
        assert user_data.id == 1

    async def test_get_user_by_email_not_found(self, test_db) -> None:
        """Ensure we get None if the user with email doesn't exist."""
        with pytest.raises(HTTPException, match=ErrorMessages.USER_INVALID):
            await UserManager.get_user_by_email(
                self.test_user["email"], test_db
            )

    async def test_get_all_users(self, test_db) -> None:
        """Test getting all users."""
        user = self.test_user.copy()
        number_of_users = 5
        for i in range(number_of_users):
            user["email"] = f"user{i}@test.com"
            await UserManager.register(user, test_db)

        users = await UserManager.get_all_users(test_db)

        assert isinstance(users, list)
        assert len(users) == number_of_users

    async def test_get_all_users_empty(self, test_db) -> None:
        """Test getting all users when there are none."""
        users = await UserManager.get_all_users(test_db)

        assert len(users) == 0

    async def test_register_with_invalid_password_format(self, test_db) -> None:
        """Test registering with an invalid password format."""
        test_data = self.test_user.copy()
        test_data["password"] = ""  # Empty password

        with pytest.raises(HTTPException) as exc_info:
            await UserManager.register(test_data, test_db)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == ErrorMessages.PASSWORD_INVALID

    async def test_register_with_none_password(self, test_db) -> None:
        """Test registering with a None password."""
        test_data = self.test_user.copy()
        del test_data["password"]  # This will cause password to be None

        with pytest.raises(HTTPException) as exc_info:
            await UserManager.register(test_data, test_db)

        assert (
            exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        assert exc_info.value.detail == ErrorMessages.PASSWORD_MISSING

    async def test_update_user_with_empty_password(self, test_db) -> None:
        """Test updating a user with an empty password."""
        # First create a user
        await UserManager.register(self.test_user, test_db)
        user = await UserManager.get_user_by_email(
            self.test_user["email"], test_db
        )

        # Try to update with empty password - should keep existing password
        user_data = UserEditRequest(
            email=self.test_user["email"],
            first_name=self.test_user["first_name"],
            last_name=self.test_user["last_name"],
            password="",  # Empty password should keep existing password
        )

        updated_user = await UserManager.update_user(
            user.id, user_data, test_db
        )
        assert updated_user is not None
        # Password should remain unchanged
        assert verify_password(
            self.test_user["password"], updated_user.password
        )

    async def test_change_password_with_invalid_format(self, test_db) -> None:
        """Test changing password with an invalid format."""
        await UserManager.register(self.test_user, test_db)

        with pytest.raises(HTTPException) as exc_info:
            await UserManager.change_password(
                1,
                UserChangePasswordRequest(password=""),  # Empty password
                test_db,
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == ErrorMessages.PASSWORD_INVALID

    async def test_change_password_with_none_password(self, test_db) -> None:
        """Test changing password with a None value."""
        await UserManager.register(self.test_user, test_db)

        # Create request without password to simulate None
        request = UserChangePasswordRequest.model_construct()
        request.password = None  # type: ignore

        with pytest.raises(HTTPException) as exc_info:
            await UserManager.change_password(1, request, test_db)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == ErrorMessages.PASSWORD_INVALID

    async def test_login_with_invalid_password_format(self, test_db) -> None:
        """Test login with an invalid password format."""
        await UserManager.register(self.test_user, test_db)

        # Mock verify_password to raise ValueError
        with pytest.raises(HTTPException) as exc_info:
            await UserManager.login(
                {"email": self.test_user["email"], "password": ""}, test_db
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == ErrorMessages.PASSWORD_INVALID

    async def test_update_user_raises_not_found(self, test_db, mocker) -> None:
        """Test update_user raises USER_NOT_FOUND if get_user_by_id is None."""
        # Mock get_user_by_id to return None
        mocker.patch(
            "app.managers.user.UserManager.get_user_by_id", return_value=None
        )

        user_data = UserEditRequest(
            email="new@email.com",
            first_name="New",
            last_name="Name",
            password="newpassword123!",  # noqa: S106
        )

        with pytest.raises(HTTPException) as exc_info:
            await UserManager.update_user(1, user_data, test_db)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == ErrorMessages.USER_NOT_FOUND

    # ----------------------- test search users method ----------------------- #
    async def test_search_users_all_fields_exact_match(self, test_db) -> None:
        """Test searching all fields with exact match."""
        # Create test users
        await UserManager.register(self.test_user, test_db)
        user2 = self.test_user.copy()
        user2["email"] = "john.doe@example.com"
        user2["first_name"] = "John"
        user2["last_name"] = "Doe"
        await UserManager.register(user2, test_db)

        # Test exact match on email
        query = await UserManager.search_users(
            "john.doe@example.com", SearchField.ALL, exact_match=True
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 1
        assert result[0].email == "john.doe@example.com"

        # Test exact match on first name
        query = await UserManager.search_users(
            "John", SearchField.ALL, exact_match=True
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 1
        assert result[0].first_name == "John"

    async def test_search_users_all_fields_partial_match(self, test_db) -> None:
        """Test searching all fields with partial match."""
        # Create test users
        await UserManager.register(self.test_user, test_db)
        user2 = self.test_user.copy()
        user2["email"] = "john.doe@example.com"
        user2["first_name"] = "John"
        user2["last_name"] = "Doe"
        await UserManager.register(user2, test_db)

        # Test partial match
        query = await UserManager.search_users(
            "john", SearchField.ALL, exact_match=False
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 1
        assert result[0].email == "john.doe@example.com"

        # Test partial match in email
        query = await UserManager.search_users(
            "example", SearchField.ALL, exact_match=False
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 1
        assert result[0].email == "john.doe@example.com"

    async def test_search_users_specific_field_exact_match(
        self, test_db
    ) -> None:
        """Test searching specific fields with exact match."""
        # Create test users
        await UserManager.register(self.test_user, test_db)
        user2 = self.test_user.copy()
        user2["email"] = "john.doe@example.com"
        user2["first_name"] = "John"
        user2["last_name"] = "Doe"
        await UserManager.register(user2, test_db)

        # Test exact match on email field
        query = await UserManager.search_users(
            "john.doe@example.com", SearchField.EMAIL, exact_match=True
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 1
        assert result[0].email == "john.doe@example.com"

        # Test exact match on first name field
        query = await UserManager.search_users(
            "John", SearchField.FIRST_NAME, exact_match=True
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 1
        assert result[0].first_name == "John"

        # Test exact match on last name field
        query = await UserManager.search_users(
            "Doe", SearchField.LAST_NAME, exact_match=True
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 1
        assert result[0].last_name == "Doe"

    async def test_search_users_specific_field_partial_match(
        self, test_db
    ) -> None:
        """Test searching specific fields with partial match."""
        # Create test users
        await UserManager.register(self.test_user, test_db)
        user2 = self.test_user.copy()
        user2["email"] = "john.doe@example.com"
        user2["first_name"] = "John"
        user2["last_name"] = "Doe"
        await UserManager.register(user2, test_db)

        # Test partial match on email field
        query = await UserManager.search_users(
            "example", SearchField.EMAIL, exact_match=False
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 1
        assert result[0].email == "john.doe@example.com"

        # Test partial match on first name field
        query = await UserManager.search_users(
            "Jo", SearchField.FIRST_NAME, exact_match=False
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 1
        assert result[0].first_name == "John"

    async def test_search_users_no_match(self, test_db) -> None:
        """Test search with no matching results."""
        # Create test users
        await UserManager.register(self.test_user, test_db)
        user2 = self.test_user.copy()
        user2["email"] = "john.doe@example.com"
        user2["first_name"] = "John"
        user2["last_name"] = "Doe"
        await UserManager.register(user2, test_db)

        # Test no match in all fields
        query = await UserManager.search_users(
            "nonexistent", SearchField.ALL, exact_match=False
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 0

        # Test no match in specific field
        query = await UserManager.search_users(
            "nonexistent", SearchField.EMAIL, exact_match=True
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 0

    async def test_search_users_case_insensitive(self, test_db) -> None:
        """Test case-insensitive search."""
        # Create test user
        await UserManager.register(self.test_user, test_db)

        # Test case-insensitive search
        query = await UserManager.search_users(
            "TEST", SearchField.FIRST_NAME, exact_match=False
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 1
        assert result[0].first_name == "Test"

        # Test with mixed case
        query = await UserManager.search_users(
            "tEsT", SearchField.FIRST_NAME, exact_match=False
        )
        result = (await test_db.execute(query)).scalars().all()
        assert len(result) == 1
        assert result[0].first_name == "Test"
