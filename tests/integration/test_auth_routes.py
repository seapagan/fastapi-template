"""Test the authentication routes of the application."""
from copy import deepcopy

import pytest

from managers.user import pwd_context
from models.enums import RoleType
from models.user import User


class TestAuthRoutes:
    """Test the authentication routes of the application."""

    # ------------------------------------------------------------------------ #
    #        some constants to clean up the code and allow easy changing       #
    # ------------------------------------------------------------------------ #
    email_fn_to_patch = "managers.user.EmailManager.template_send"
    register_path = "/register"
    login_path = "/login"

    test_user = {
        "email": "testuser@usertest.com",
        "first_name": "Test",
        "last_name": "User",
        "password": pwd_context.hash("test12345!"),
        "verified": True,
    }

    # ------------------------------------------------------------------------ #
    #                          test '/register' route                          #
    # ------------------------------------------------------------------------ #
    @pytest.mark.asyncio
    async def test_register_new_user(self, test_app, db, mocker):
        """Ensure a new user can register."""
        # disable email sending by mocking the function
        mock_send = mocker.patch(self.email_fn_to_patch)

        post_body = {
            "email": "testuser@testuser.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "test12345!",
        }
        response = test_app.post(
            self.register_path,
            json=post_body,
        )

        assert response.status_code == 201
        assert list(response.json().keys()) == ["token", "refresh"]
        assert type(response.json()["token"]) is str
        assert type(response.json()["refresh"]) is str

        users_data = await db.fetch_one(User.select())
        assert users_data["email"] == post_body["email"]
        assert users_data["first_name"] == post_body["first_name"]
        assert users_data["last_name"] == post_body["last_name"]
        assert users_data["password"] != post_body["password"]
        assert users_data["verified"] is False
        assert users_data["role"] == RoleType.user

        mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_password_is_stored_hashed(self, test_app, db, mocker):
        """Ensure that the raw password is not stored in the database."""
        # disable email sending by mocking the function
        _ = mocker.patch(self.email_fn_to_patch)

        post_body = {
            "email": "testuser@testuser.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "test12345!",
        }
        test_app.post(
            self.register_path,
            json=post_body,
        )

        user_from_db = await db.fetch_one(
            User.select().where(User.c.email == post_body["email"])
        )
        assert user_from_db["password"] != post_body["password"]
        assert pwd_context.verify(
            post_body["password"], user_from_db["password"]
        )

    @pytest.mark.asyncio
    async def test_register_new_user_with_bad_email(self, test_app, db, mocker):
        """Ensure an invalid email address fails, and no email is sent."""
        # mock the email sending function
        mock_send = mocker.patch(self.email_fn_to_patch)

        response = test_app.post(
            self.register_path,
            json={
                "email": "bad_email",
                "first_name": "Test",
                "last_name": "User",
                "password": "test12345!",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "This email address is not valid"

        users_from_db = await db.fetch_all(User.select())
        assert len(users_from_db) == 0

        mock_send.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "post_body",
        [
            {},
            {
                "email": "",
                "first_name": "Test",
                "last_name": "User",
                "password": "test12345!",
            },
            {
                "email": "email@testuser.com",
                "first_name": "",
                "last_name": "User",
                "password": "test12345!",
            },
            {
                "email": "email@testuser.com",
                "first_name": "Test",
                "last_name": "",
                "password": "test12345!",
            },
            {
                "email": "email@testuser.com",
                "first_name": "Test",
                "last_name": "User",
                "password": "",
            },
        ],
    )
    async def test_register_new_user_with_missing_data(
        self, test_app, db, mocker, post_body
    ):
        """Ensure registering with missing data fails, and no email is sent."""
        # mock the email sending function
        mock_send = mocker.patch(self.email_fn_to_patch)

        response = test_app.post(self.register_path, json=post_body)

        assert response.status_code == 400 or 422

        users_from_db = await db.fetch_all(User.select())
        assert len(users_from_db) == 0

        mock_send.assert_not_called()

    # ------------------------------------------------------------------------ #
    #                            test '/login' route                           #
    # ------------------------------------------------------------------------ #
    @pytest.mark.asyncio
    async def test_cant_login_before_verifying_email(self, test_app, db):
        """Ensure a new user has to validate email before logging in."""
        my_user = deepcopy(self.test_user)
        my_user["verified"] = False
        _ = await db.execute(User.insert(), values=my_user)

        response = test_app.post(
            self.login_path,
            json={
                "email": self.test_user["email"],
                "password": "test12345!",
            },
        )

        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "You need to verify your Email before logging in"
        )

    @pytest.mark.asyncio
    async def test_verified_user_can_login(self, test_app, db):
        """Ensure a validated user can log in."""
        _ = await db.execute(User.insert(), values=self.test_user)

        response = test_app.post(
            self.login_path,
            json={
                "email": self.test_user["email"],
                "password": "test12345!",
            },
        )

        assert response.status_code == 200
        assert list(response.json().keys()) == ["token", "refresh"]
        assert type(response.json()["token"]) is str
        assert type(response.json()["refresh"]) is str

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "post_body",
        [
            {
                "email": "notregistered@usertest.com",
                "password": "test12345!",
            },
            {
                "email": "testuser@usertest.com",
                "password": "thisiswrong!",
            },
        ],
    )
    async def test_cant_login_with_wrong_email_or_password(
        self, test_app, db, post_body
    ):
        """Ensure the user cant login with wrong email or password."""
        _ = await db.execute(User.insert(), values=self.test_user)

        response = test_app.post(
            self.login_path,
            json=post_body,
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Wrong email or password"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "post_body",
        [
            {},
            {
                "password": "test12345!",
            },
            {
                "email": "testuser@usertest.com",
            },
        ],
    )
    async def test_cant_login_with_missing_email_or_password(
        self, test_app, db, post_body
    ):
        """Ensure the user cant login with wrong email or password."""
        _ = await db.execute(User.insert(), values=self.test_user)

        response = test_app.post(
            self.login_path,
            json=post_body,
        )

        assert response.status_code == 422
        print(response.json())
        assert "value_error.missing" in str(response.json()["detail"])
