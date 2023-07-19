"""Test the home resource routes."""
import pytest


@pytest.mark.integration()
class TestHomeRoutes:
    """Test the home resource routes."""

    def test_root_json(self, test_app):
        """Test the root route returns a JSON response."""
        response = test_app.get("/")
        assert response.status_code == 200
        assert list(response.json().keys()) == ["info", "repository"]

    def test_root_html(self, test_app):
        """Test the root route returns an HTML response when requested."""
        response = test_app.get("/", headers={"Accept": "text/html"})
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.text.startswith("<!DOCTYPE html>")
