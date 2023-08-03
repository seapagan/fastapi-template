"""Test the home resource routes."""
import pytest


@pytest.mark.integration()
class TestHomeRoutes:
    """Test the home resource routes."""

    @pytest.mark.asyncio()
    async def test_root_json(self, client):
        """Test the root route returns a JSON response."""
        response = await client.get("/")
        assert response.status_code == 200
        assert list(response.json().keys()) == ["info", "repository"]

    @pytest.mark.asyncio()
    async def test_root_html(self, client):
        """Test the root route returns an HTML response when requested."""
        response = await client.get("/", headers={"Accept": "text/html"})
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        assert response.text.startswith("<!DOCTYPE html>")
