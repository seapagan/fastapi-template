"""Test the User Model.

Just checking the __repr__ at this time.
"""

from app.models.user import User


class TestUserModel:
    """Test the User Model."""

    def test_repr(self) -> None:
        """Test the __repr__ method."""
        user = User(
            id=1, email="test@test.com", first_name="test", last_name="user"
        )

        assert repr(user) == 'User(1, "test user")'
