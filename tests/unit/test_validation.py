"""Test the Settings module validation functions."""

from app.config.settings import Settings


class TestValidateSettings:
    """Test the Settings module validation functions."""

    test_root = "/api/v1"

    def test_api_root_ends_with_slash(self) -> None:
        """A trailing slash should be removed from the api_root."""
        settings = Settings(api_root=f"{self.test_root}/")
        assert (
            settings.api_root == self.test_root
        ), "api_root should have trailing slash removed"

    def test_api_root_without_trailing_slash(self) -> None:
        """Good api_root should remain unchanged."""
        settings = Settings(api_root=self.test_root)
        assert (
            settings.api_root == self.test_root
        ), "api_root should remain unchanged"

    def test_api_root_empty_string(self) -> None:
        """Empty string should be handled correctly."""
        settings = Settings(api_root="")
        assert (
            settings.api_root == ""
        ), "api_root should handle empty strings correctly"
