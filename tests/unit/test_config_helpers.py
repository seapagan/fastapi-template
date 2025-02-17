"""Test config/helpers.py."""

import logging
from pathlib import Path

import pytest

from app.config.helpers import (
    LICENCES,
    TEMPLATE,
    get_api_details,
    get_api_version,
    get_config_path,
    get_toml_path,
)


@pytest.mark.unit
class TestConfigHelpers:
    """Test the helpers used by the config module."""

    mock_load_rtoml = "app.config.helpers.rtoml.load"

    def test_get_toml_path(self, mocker) -> None:
        """Test we get the correct toml path."""
        mocker.patch(
            "app.config.helpers.resources.files",
            return_value="/test/path/app",
        )
        assert get_toml_path() == Path("/test/path/pyproject.toml")

    def test_get_config_path(self, mocker) -> None:
        """Test we get the correct config path."""
        mocker.patch(
            "app.config.helpers.resources.files",
            return_value="/test/path/app",
        )
        assert get_config_path() == Path("/test/path/app/config/metadata.py")

    def test_get_api_version(self, mocker) -> None:
        """Test we get the API version."""
        mocker.patch(
            self.mock_load_rtoml,
            return_value={"project": {"version": "1.2.3"}},
        )
        assert get_api_version() == "1.2.3"

    def test_get_api_version_missing_toml(self, mocker, caplog) -> None:
        """Test we exit when the toml file is missing."""
        mocker.patch(self.mock_load_rtoml, side_effect=FileNotFoundError)

        caplog.set_level(logging.ERROR)

        with pytest.raises(SystemExit, match="2"):
            get_api_version()
        log_messages = [
            (record.levelname, record.message) for record in caplog.records
        ]

        assert len(log_messages) == 1
        assert any(
            record.levelname == "ERROR"
            and "Cannot read the pyproject.toml file" in record.message
            for record in caplog.records
        ), "Expected error log not found"

    def test_get_api_version_missing_version(self, mocker, caplog) -> None:
        """Test we exit when the version is missing."""
        mocker.patch(
            self.mock_load_rtoml,
            return_value={"tool": {"poetry": {"version:": ""}}},
        )
        with pytest.raises(SystemExit, match="2"):
            get_api_version()

        log_messages = [
            (record.levelname, record.message) for record in caplog.records
        ]

        assert len(log_messages) == 1
        assert (
            "ERROR",
            "Cannot find the API version in the pyproject.toml file",
        ) in log_messages, "Expected error log not found"

    def test_get_api_version_missing_key(self, mocker, caplog) -> None:
        """Test we exit when the key is missing."""
        mocker.patch(
            self.mock_load_rtoml,
            return_value={"tool": {"poetry": {}}},
        )

        caplog.set_level(logging.ERROR)

        with pytest.raises(SystemExit, match="2"):
            get_api_version()

        log_messages = [
            (record.levelname, record.message) for record in caplog.records
        ]

        assert len(log_messages) == 1
        assert (
            "ERROR",
            "Cannot find the API version in the pyproject.toml file",
        ) in log_messages

    def test_get_api_details(self, mocker, capfd) -> None:
        """Test we get the API details."""
        mocker.patch(
            self.mock_load_rtoml,
            return_value={
                "project": {
                    "name": "test_name",
                    "description": "test_desc",
                    "authors": [
                        {
                            "name": "Grant Ramsay",
                            "email": "seapagan@gmail.com",
                        }
                    ],
                }
            },
        )
        details = get_api_details()

        assert isinstance(details, tuple)
        assert details == (
            "test_name",
            "test_desc",
            [
                {
                    "name": "Grant Ramsay",
                    "email": "seapagan@gmail.com",
                }
            ],
        )

    def test_get_api_details_author_not_list(self, mocker, capfd) -> None:
        """Test we get the API details."""
        mocker.patch(
            self.mock_load_rtoml,
            return_value={
                "project": {
                    "name": "test_name",
                    "description": "test_desc",
                    "authors": {
                        "name": "Grant Ramsay",
                        "email": "seapagan@gmail.com",
                    },
                }
            },
        )
        details = get_api_details()

        assert isinstance(details, tuple)
        assert isinstance(details[2], list)
        assert details == (
            "test_name",
            "test_desc",
            [
                {
                    "name": "Grant Ramsay",
                    "email": "seapagan@gmail.com",
                }
            ],
        )

    def test_get_api_details_authors_is_list(self, mocker) -> None:
        """Authors should be converted to a list if not already."""
        mocker.patch(
            self.mock_load_rtoml,
            return_value={
                "project": {
                    "name": "test_name",
                    "description": "test_desc",
                    "authors": [
                        {
                            "name": "Grant Ramsay",
                            "email": "seapagan@gmail.com",
                        }
                    ],
                }
            },
        )
        _, _, authors = get_api_details()
        assert isinstance(authors, list)

    @pytest.mark.parametrize(
        "missing_keys",
        [
            {"description": "test_desc", "authors": ["test_authors"]},
            {"name": "test_name", "authors": ["test_authors"]},
            {"name": "test_name", "description": "test_desc"},
        ],
    )
    def test_get_api_details_missing_key(
        self, mocker, caplog, missing_keys
    ) -> None:
        """We should return an Error if any details are missing."""
        mocker.patch(
            self.mock_load_rtoml,
            return_value={
                "tool": {
                    "poetry": missing_keys,
                }
            },
        )

        caplog.set_level(logging.ERROR)

        with pytest.raises(SystemExit, match="2"):
            get_api_details()

        logger_messages = [
            (record.levelname, record.message) for record in caplog.records
        ]
        assert len(logger_messages) == 1
        assert (
            "ERROR",
            "Missing name/description or authors in the pyproject.toml file",
        ) in logger_messages

    def test_get_api_details_missing_toml(self, mocker, caplog) -> None:
        """Test we exit when the toml file is missing."""
        mocker.patch(self.mock_load_rtoml, side_effect=FileNotFoundError)

        caplog.set_level(logging.ERROR)

        with pytest.raises(SystemExit, match="2"):
            get_api_details()

        assert len(caplog.records) == 1
        assert any(
            record.levelname == "ERROR"
            and "Cannot read the pyproject.toml file" in record.message
            for record in caplog.records
        )

    def test_licences_structure(self) -> None:
        """Test the licences structure."""
        assert isinstance(LICENCES, list)

        for licence in LICENCES:
            assert isinstance(licence, dict)
            assert [*licence] == ["name", "url"]

            assert all(isinstance(value, str) for value in licence.values())

    def test_template_structure(self) -> None:
        """Test the template structure.

        Just a basic test to ensure the template is a string and not empty.

        I may look at testing the contained 'MetadataBase' class structure in
        the future, since this is pretty important to get right.
        """
        assert isinstance(TEMPLATE, str)
        assert TEMPLATE != ""
