"""Integration tests for API key routes."""

from typing import Any, Union
from uuid import UUID

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.helpers import hash_password
from app.managers.auth import AuthManager
from app.models.enums import RoleType
from app.models.user import User

# this should become a config setting later, so we can change the route and
# tests in one place.
API_KEY_ROUTE = "/users/keys"


@pytest.mark.integration
class TestApiKeyRoutes:
    """Test the API key routes of the application."""

    def get_test_user(
        self,
        *,
        hashed: bool = True,
        admin: bool = False,
        email: Union[str, None] = None,
    ) -> dict[str, Any]:
        """Return a test user dictionary."""
        return {
            "email": email or "testuser@usertest.com",
            "first_name": "Test",
            "last_name": "User",
            "password": hash_password("test12345!") if hashed else "test12345!",
            "verified": True,
            "role": RoleType.admin if admin else RoleType.user,
        }

    @pytest.mark.asyncio
    async def test_create_api_key(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test creating a new API key."""
        # Create and login a user
        test_user = User(**self.get_test_user())
        test_db.add(test_user)
        await test_db.commit()
        token = AuthManager.encode_token(test_user)

        # Create API key
        response = await client.post(
            API_KEY_ROUTE,
            json={"name": "Test Key", "scopes": ["read:users", "write:users"]},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "key" in data
        assert data["name"] == "Test Key"
        assert data["is_active"] is True
        assert data["scopes"] == ["read:users", "write:users"]
        assert isinstance(UUID(data["id"]), UUID)

    @pytest.mark.asyncio
    async def test_list_api_keys(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test listing API keys."""
        # Create and login a user
        test_user = User(**self.get_test_user())
        test_db.add(test_user)
        await test_db.commit()
        token = AuthManager.encode_token(test_user)

        # Create an API key first
        await client.post(
            API_KEY_ROUTE,
            json={"name": "Test Key 1", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        await client.post(
            API_KEY_ROUTE,
            json={"name": "Test Key 2", "scopes": ["write:users"]},
            headers={"Authorization": f"Bearer {token}"},
        )

        # List API keys
        response = await client.get(
            API_KEY_ROUTE,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2  # noqa: PLR2004
        assert all(isinstance(UUID(key["id"]), UUID) for key in data)
        assert "key" not in data[0]  # Raw key should not be included in list
        assert "key" not in data[1]

    @pytest.mark.asyncio
    async def test_get_specific_api_key(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test getting a specific API key."""
        # Create and login a user
        test_user = User(**self.get_test_user())
        test_db.add(test_user)
        await test_db.commit()
        token = AuthManager.encode_token(test_user)

        # Create an API key
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "Test Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        key_id = create_response.json()["id"]

        # Get the specific key
        response = await client.get(
            f"{API_KEY_ROUTE}/{key_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == key_id
        assert data["name"] == "Test Key"
        assert "key" not in data  # Raw key should not be included in get

    @pytest.mark.asyncio
    async def test_update_api_key(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test updating an API key."""
        # Create and login a user
        test_user = User(**self.get_test_user())
        test_db.add(test_user)
        await test_db.commit()
        token = AuthManager.encode_token(test_user)

        # Create an API key
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "Test Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        key_id = create_response.json()["id"]

        # Update the key
        response = await client.patch(
            f"{API_KEY_ROUTE}/{key_id}",
            json={"name": "Updated Key", "is_active": False},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Key"
        assert data["is_active"] is False

    @pytest.mark.asyncio
    async def test_delete_api_key(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test deleting an API key."""
        # Create and login a user
        test_user = User(**self.get_test_user())
        test_db.add(test_user)
        await test_db.commit()
        token = AuthManager.encode_token(test_user)

        # Create an API key
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "Test Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        key_id = create_response.json()["id"]

        # Delete the key
        response = await client.delete(
            f"{API_KEY_ROUTE}/{key_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify key is deleted
        get_response = await client.get(
            f"{API_KEY_ROUTE}/{key_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_cannot_access_others_api_keys(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test that a user cannot access another user's API keys."""
        # Create two users
        user1 = User(**self.get_test_user())
        user2 = User(**{**self.get_test_user(), "email": "user2@test.com"})
        test_db.add(user1)
        test_db.add(user2)
        await test_db.commit()

        # Get tokens for both users
        token1 = AuthManager.encode_token(user1)
        token2 = AuthManager.encode_token(user2)

        # Create an API key for user1
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "User1 Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {token1}"},
        )
        key_id = create_response.json()["id"]

        # Try to access user1's key with user2's token
        response = await client.get(
            f"{API_KEY_ROUTE}/{key_id}",
            headers={"Authorization": f"Bearer {token2}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_api_key_no_auth(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test creating an API key without authentication."""
        response = await client.post(
            API_KEY_ROUTE,
            json={"name": "Test Key", "scopes": ["read:users"]},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_update_nonexistent_api_key(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test updating a non-existent API key."""
        # Create and login a user
        test_user = User(**self.get_test_user())
        test_db.add(test_user)
        await test_db.commit()
        token = AuthManager.encode_token(test_user)

        # Try to update a non-existent key
        response = await client.patch(
            f"{API_KEY_ROUTE}/00000000-0000-0000-0000-000000000000",
            json={"name": "Updated Key", "is_active": False},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "API key not found"

    @pytest.mark.asyncio
    async def test_delete_nonexistent_api_key(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test deleting a non-existent API key."""
        # Create and login a user
        test_user = User(**self.get_test_user())
        test_db.add(test_user)
        await test_db.commit()
        token = AuthManager.encode_token(test_user)

        # Try to delete a non-existent key
        response = await client.delete(
            f"{API_KEY_ROUTE}/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "API key not found"

    @pytest.mark.asyncio
    async def test_create_api_key_invalid_request(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test creating an API key with invalid request data."""
        # Create and login a user
        test_user = User(**self.get_test_user())
        test_db.add(test_user)
        await test_db.commit()
        token = AuthManager.encode_token(test_user)

        # Test with missing required field
        response = await client.post(
            API_KEY_ROUTE,
            json={"scopes": ["read:users"]},  # Missing 'name' field
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test with invalid scopes format
        response = await client.post(
            API_KEY_ROUTE,
            json={
                "name": "Test Key",
                "scopes": "invalid",
            },  # scopes should be a list
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_update_api_key_invalid_request(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test updating an API key with invalid request data."""
        # Create and login a user
        test_user = User(**self.get_test_user())
        test_db.add(test_user)
        await test_db.commit()
        token = AuthManager.encode_token(test_user)

        # Create an API key first
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "Test Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        key_id = create_response.json()["id"]

        # Test with invalid is_active type
        response = await client.patch(
            f"{API_KEY_ROUTE}/{key_id}",
            json={
                "name": "Updated Key",
                "is_active": "invalid",
            },  # should be boolean
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test with invalid name length
        response = await client.patch(
            f"{API_KEY_ROUTE}/{key_id}",
            json={"name": ""},  # Empty name is not allowed
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test with empty update data
        response = await client.patch(
            f"{API_KEY_ROUTE}/{key_id}",
            json={},  # Empty update data
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert (
            "At least one field must be provided for update"
            in response.json()["detail"]
        )

    @pytest.mark.asyncio
    async def test_update_api_key_update_failure(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ) -> None:
        """Test updating an API key when the update operation fails."""
        # Create and login a user
        test_user = User(**self.get_test_user())
        test_db.add(test_user)
        await test_db.commit()
        token = AuthManager.encode_token(test_user)

        # Create an API key
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "Test Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        key_id = create_response.json()["id"]

        # Mock update_api_key_ to return None (simulating update failure)
        mocker.patch("app.resources.api_key.update_api_key_", return_value=None)

        # Try to update the key
        response = await client.patch(
            f"{API_KEY_ROUTE}/{key_id}",
            json={"name": "Updated Key"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "API key not found"

    @pytest.mark.asyncio
    async def test_admin_can_list_user_api_keys(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test that an admin can list another user's API key."""
        # Create a regular user and an admin
        regular_user = User(**self.get_test_user(email="regular@test.com"))
        admin_user = User(
            **self.get_test_user(admin=True, email="admin@test.com")
        )
        test_db.add(regular_user)
        test_db.add(admin_user)
        await test_db.commit()

        # Get tokens
        user_token = AuthManager.encode_token(regular_user)
        admin_token = AuthManager.encode_token(admin_user)

        # Create API keys for the regular user
        await client.post(
            API_KEY_ROUTE,
            json={"name": "User Key 1", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        await client.post(
            API_KEY_ROUTE,
            json={"name": "User Key 2", "scopes": ["write:users"]},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        # Admin lists the user's API keys
        response = await client.get(
            f"{API_KEY_ROUTE}/by-user/{regular_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2  # noqa: PLR2004
        assert all(isinstance(UUID(key["id"]), UUID) for key in data)
        assert "key" not in data[0]
        assert "key" not in data[1]

    @pytest.mark.asyncio
    async def test_admin_can_update_user_api_key(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test that an admin can update another user's API key."""
        # Create a regular user and an admin
        regular_user = User(**self.get_test_user(email="regular@test.com"))
        admin_user = User(
            **self.get_test_user(admin=True, email="admin@test.com")
        )
        test_db.add(regular_user)
        test_db.add(admin_user)
        await test_db.commit()

        # Get tokens
        user_token = AuthManager.encode_token(regular_user)
        admin_token = AuthManager.encode_token(admin_user)

        # Create an API key for the regular user
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "User Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        key_id = create_response.json()["id"]

        # Admin updates the user's API key
        response = await client.patch(
            f"{API_KEY_ROUTE}/by-user/{regular_user.id}/{key_id}",
            json={"name": "Updated By Admin", "is_active": False},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated By Admin"
        assert data["is_active"] is False

    @pytest.mark.asyncio
    async def test_admin_can_delete_user_api_key(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test that an admin can delete another user's API key."""
        # Create a regular user and an admin
        regular_user = User(**self.get_test_user(email="regular@test.com"))
        admin_user = User(
            **self.get_test_user(admin=True, email="admin@test.com")
        )
        test_db.add(regular_user)
        test_db.add(admin_user)
        await test_db.commit()

        # Get tokens
        user_token = AuthManager.encode_token(regular_user)
        admin_token = AuthManager.encode_token(admin_user)

        # Create an API key for the regular user
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "User Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        key_id = create_response.json()["id"]

        # Admin deletes the user's API key
        response = await client.delete(
            f"{API_KEY_ROUTE}/by-user/{regular_user.id}/{key_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify key is deleted
        get_response = await client.get(
            f"{API_KEY_ROUTE}/{key_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_non_admin_cannot_access_admin_api_key_routes(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test that non-admin users cannot access admin API key routes."""
        # Create two regular users
        user1 = User(**self.get_test_user(email="user1@test.com"))
        user2 = User(**self.get_test_user(email="user2@test.com"))
        test_db.add(user1)
        test_db.add(user2)
        await test_db.commit()

        # Get token for user1
        user1_token = AuthManager.encode_token(user1)

        # Create an API key for user2
        user2_token = AuthManager.encode_token(user2)
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "User2 Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        key_id = create_response.json()["id"]

        # Try to list user2's keys
        list_response = await client.get(
            f"{API_KEY_ROUTE}/by-user/{user2.id}",
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert list_response.status_code == status.HTTP_403_FORBIDDEN

        # Try to update user2's key
        update_response = await client.patch(
            f"{API_KEY_ROUTE}/by-user/{user2.id}/{key_id}",
            json={"name": "Updated Name"},
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert update_response.status_code == status.HTTP_403_FORBIDDEN

        # Try to delete user2's key
        delete_response = await client.delete(
            f"{API_KEY_ROUTE}/by-user/{user2.id}/{key_id}",
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert delete_response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_admin_update_key_wrong_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test admin trying to update a key with wrong user ID."""
        # Create two regular users and an admin
        user1 = User(**self.get_test_user(email="user1@test.com"))
        user2 = User(**self.get_test_user(email="user2@test.com"))
        admin_user = User(
            **self.get_test_user(admin=True, email="admin@test.com")
        )
        test_db.add(user1)
        test_db.add(user2)
        test_db.add(admin_user)
        await test_db.commit()

        # Get tokens
        user1_token = AuthManager.encode_token(user1)
        admin_token = AuthManager.encode_token(admin_user)

        # Create an API key for user1
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "User1 Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        key_id = create_response.json()["id"]

        # Admin tries to update the key but associates it with user2
        response = await client.patch(
            f"{API_KEY_ROUTE}/by-user/{user2.id}/{key_id}",
            json={"name": "Updated Name"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "API key not found"

    @pytest.mark.asyncio
    async def test_admin_update_key_no_fields(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test admin trying to update a key without providing any fields."""
        # Create a regular user and an admin
        regular_user = User(**self.get_test_user(email="regular@test.com"))
        admin_user = User(
            **self.get_test_user(admin=True, email="admin@test.com")
        )
        test_db.add(regular_user)
        test_db.add(admin_user)
        await test_db.commit()

        # Get tokens
        user_token = AuthManager.encode_token(regular_user)
        admin_token = AuthManager.encode_token(admin_user)

        # Create an API key for the regular user
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "User Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        key_id = create_response.json()["id"]

        # Admin tries to update the key without providing any fields
        response = await client.patch(
            f"{API_KEY_ROUTE}/by-user/{regular_user.id}/{key_id}",
            json={},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert (
            response.json()["detail"]
            == "At least one field must be provided for update"
        )

    @pytest.mark.asyncio
    async def test_admin_delete_key_wrong_user(
        self, client: AsyncClient, test_db: AsyncSession
    ) -> None:
        """Test admin trying to delete a key with wrong user ID."""
        # Create two regular users and an admin
        user1 = User(**self.get_test_user(email="user1@test.com"))
        user2 = User(**self.get_test_user(email="user2@test.com"))
        admin_user = User(
            **self.get_test_user(admin=True, email="admin@test.com")
        )
        test_db.add(user1)
        test_db.add(user2)
        test_db.add(admin_user)
        await test_db.commit()

        # Get tokens
        user1_token = AuthManager.encode_token(user1)
        admin_token = AuthManager.encode_token(admin_user)

        # Create an API key for user1
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "User1 Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        key_id = create_response.json()["id"]

        # Admin tries to delete the key but associates it with user2
        response = await client.delete(
            f"{API_KEY_ROUTE}/by-user/{user2.id}/{key_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "API key not found"

    @pytest.mark.asyncio
    async def test_admin_update_key_update_failure(
        self, client: AsyncClient, test_db: AsyncSession, mocker
    ) -> None:
        """Test admin updating an API key when the update operation fails."""
        # Create a regular user and an admin
        regular_user = User(**self.get_test_user(email="regular@test.com"))
        admin_user = User(
            **self.get_test_user(admin=True, email="admin@test.com")
        )
        test_db.add(regular_user)
        test_db.add(admin_user)
        await test_db.commit()

        # Get tokens
        user_token = AuthManager.encode_token(regular_user)
        admin_token = AuthManager.encode_token(admin_user)

        # Create an API key for the regular user
        create_response = await client.post(
            API_KEY_ROUTE,
            json={"name": "User Key", "scopes": ["read:users"]},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        key_id = create_response.json()["id"]

        # Mock update_api_key_ to return None (simulating update failure)
        mocker.patch("app.resources.api_key.update_api_key_", return_value=None)

        # Admin tries to update the key
        response = await client.patch(
            f"{API_KEY_ROUTE}/by-user/{regular_user.id}/{key_id}",
            json={"name": "Updated Name"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "API key not found"
