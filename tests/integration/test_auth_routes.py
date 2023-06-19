"""Test the authentication routes of the application."""
from copy import deepcopy

import pytest

from app.managers.auth import AuthManager
from app.managers.user import pwd_context
from app.models.enums import RoleType
from app.models.user import User


@pytest.mark.integration()
class TestAuthRoutes:
    """Test the authentication routes of the application."""

    # ------------------------------------------------------------------------ #
    #        some constants to clean up the code and allow easy changing       #
    # ------------------------------------------------------------------------ #
    email_fn_to_patch = "app.managers.user.EmailManager.template_send"
    register_path = "/register"
    login_path = "/login"

    test_user = {
        "email": "testuser@usertest.com",
        "first_name": "Test",
        "last_name": "User",
        "password": pwd_context.hash("test12345!"),
        "verified": True,
    }

    test_unverified_user = {
        **test_user,
        "verified": False,
    }

    test_banned_user = {
        **test_user,
        "banned": True,
    }

    # ------------------------------------------------------------------------ #
    #                          test '/register' route                          #
    # ------------------------------------------------------------------------ #
    @pytest.mark.asyncio()
    async def test_register_new_user(self, test_app, get_db, mocker):
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
        assert isinstance(response.json()["token"], str)
        assert isinstance(response.json()["refresh"], str)

        users_data = await get_db.fetch_one(User.select())
        assert users_data["email"] == post_body["email"]
        assert users_data["first_name"] == post_body["first_name"]
        assert users_data["last_name"] == post_body["last_name"]
        assert users_data["password"] != post_body["password"]
        assert users_data["verified"] is False
        assert users_data["role"] == RoleType.user

        mock_send.assert_called_once()

    @pytest.mark.asyncio()
    async def test_password_is_stored_hashed(self, test_app, get_db, mocker):
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

        user_from_db = await get_db.fetch_one(
            User.select().where(User.c.email == post_body["email"])
        )
        assert user_from_db["password"] != post_body["password"]
        assert pwd_context.verify(
            post_body["password"], user_from_db["password"]
        )

    @pytest.mark.asyncio()
    async def test_register_new_user_with_bad_email(
        self, test_app, get_db, mocker
    ):
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

        users_from_db = await get_db.fetch_all(User.select())
        assert len(users_from_db) == 0

        mock_send.assert_not_called()

    @pytest.mark.asyncio()
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
        self, test_app, get_db, mocker, post_body
    ):
        """Ensure registering with missing data fails, and no email is sent."""
        # mock the email sending function
        mock_send = mocker.patch(self.email_fn_to_patch)

        response = test_app.post(self.register_path, json=post_body)

        assert response.status_code in (400, 422)

        users_from_db = await get_db.fetch_all(User.select())
        assert len(users_from_db) == 0

        mock_send.assert_not_called()

    # ------------------------------------------------------------------------ #
    #                            test '/login' route                           #
    # ------------------------------------------------------------------------ #
    @pytest.mark.asyncio()
    async def test_cant_login_before_verifying_email(self, test_app, get_db):
        """Ensure a new user has to validate email before logging in."""
        my_user = deepcopy(self.test_user)
        my_user["verified"] = False
        _ = await get_db.execute(User.insert(), values=my_user)

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

    @pytest.mark.asyncio()
    async def test_verified_user_can_login(self, test_app, get_db):
        """Ensure a validated user can log in."""
        _ = await get_db.execute(User.insert(), values=self.test_user)

        response = test_app.post(
            self.login_path,
            json={
                "email": self.test_user["email"],
                "password": "test12345!",
            },
        )

        assert response.status_code == 200
        assert list(response.json().keys()) == ["token", "refresh"]
        assert isinstance(response.json()["token"], str)
        assert isinstance(response.json()["refresh"], str)

    @pytest.mark.asyncio()
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
        self, test_app, get_db, post_body
    ):
        """Ensure the user cant login with wrong email or password."""
        _ = await get_db.execute(User.insert(), values=self.test_user)

        response = test_app.post(
            self.login_path,
            json=post_body,
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Wrong email or password"

    @pytest.mark.asyncio()
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
        self, test_app, get_db, post_body
    ):
        """Ensure the user cant login with missing email or password."""
        _ = await get_db.execute(User.insert(), values=self.test_user)

        response = test_app.post(
            self.login_path,
            json=post_body,
        )

        assert response.status_code == 422
        assert "value_error.missing" in str(response.json()["detail"])

    @pytest.mark.asyncio()
    async def test_cant_login_with_unverified_email(self, test_app, get_db):
        """Ensure the user cant login with unverified email."""
        _ = await get_db.execute(
            User.insert(), values=self.test_unverified_user
        )

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

    @pytest.mark.asyncio()
    async def test_cant_login_with_banned_user(self, test_app, get_db):
        """Ensure the user cant login with banned user."""
        _ = await get_db.execute(User.insert(), values=self.test_banned_user)

        response = test_app.post(
            self.login_path,
            json={
                "email": self.test_banned_user["email"],
                "password": "test12345!",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Wrong email or password"

    # ------------------------------------------------------------------------ #
    #                           test '/refresh' route                          #
    # ------------------------------------------------------------------------ #

    @pytest.mark.asyncio()
    async def test_refresh_token(self, test_app, get_db):
        """Ensure the user can refresh the token."""
        _ = await get_db.execute(User.insert(), values=self.test_user)

        login_response = test_app.post(
            self.login_path,
            json={
                "email": self.test_user["email"],
                "password": "test12345!",
            },
        )

        refresh_response = test_app.post(
            "/refresh",
            json={
                "refresh": login_response.json()["refresh"],
            },
        )

        assert refresh_response.status_code == 200
        assert list(refresh_response.json().keys()) == ["token"]
        assert isinstance(refresh_response.json()["token"], str)

    @pytest.mark.asyncio()
    async def test_cant_refresh_token_with_invalid_refresh_token(
        self, test_app, get_db
    ):
        """Ensure the user cant refresh the token with invalid refresh token."""
        _ = await get_db.execute(User.insert(), values=self.test_user)

        refresh_response = test_app.post(
            "/refresh",
            json={
                "refresh": "invalid_refresh_token",
            },
        )

        assert refresh_response.status_code == 401
        assert refresh_response.json()["detail"] == "That token is Invalid"

    # ------------------------------------------------------------------------ #
    #                           test '/verify' route                           #
    # ------------------------------------------------------------------------ #

    @pytest.mark.asyncio()
    async def test_verify_user(self, test_app, get_db):
        """Test we can verify a user."""
        _ = await get_db.execute(
            User.insert(), values={**self.test_user, "verified": False}
        )
        verification_token = AuthManager.encode_verify_token({"id": 1})

        response = test_app.get(f"/verify/?code={verification_token}")

        assert response.status_code == 200
        assert response.json()["detail"] == "User succesfully Verified"

    @pytest.mark.parametrize(
        "verification_token",
        ["BADBEEF", ""],
    )
    @pytest.mark.asyncio()
    async def test_verify_bad_token(self, test_app, get_db, verification_token):
        """Ensure a bad token cant be used to verify a user."""
        _ = await get_db.execute(
            User.insert(), values={**self.test_user, "verified": False}
        )
        response = test_app.get(f"/verify/?code={verification_token}")

        assert response.status_code == 401
        assert response.json()["detail"] == "That token is Invalid"
