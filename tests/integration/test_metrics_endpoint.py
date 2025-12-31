"""Integration tests for Prometheus metrics endpoint."""

import pytest
from fastapi import status

from app.database.helpers import hash_password
from app.metrics import METRIC_NAMESPACE
from app.models.user import User


@pytest.mark.integration
class TestMetricsEndpoint:
    """Test the Prometheus metrics endpoint."""

    # Test user data
    test_password = "test12345!"  # noqa: S105
    test_user: dict[str, str | bool] = {
        "email": "metricstest@usertest.com",
        "first_name": "Metrics",
        "last_name": "Test",
        "password": hash_password(test_password),
        "verified": True,
    }

    @staticmethod
    def _extract_metric_value(content: str, metric_label: str) -> int:
        """Extract the numeric value of a metric from Prometheus output.

        Args:
            content: The full Prometheus metrics text output
            metric_label: The metric label to search for (e.g.,
                'login_attempts_total{status="success"}')

        Returns:
            The numeric value of the metric, or 0 if not found
        """
        for line in content.split("\n"):
            if line.startswith(metric_label):
                # Line format: metric_label value
                parts = line.split()
                if len(parts) >= 2:  # noqa: PLR2004
                    return int(float(parts[1]))
        return 0

    @pytest.mark.asyncio
    async def test_metrics_endpoint_accessible(self, client) -> None:
        """Test that the metrics endpoint is accessible when enabled."""
        response = await client.get("/metrics")
        assert response.status_code == status.HTTP_200_OK
        assert "text/plain" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_metrics_have_correct_prefix(self, client) -> None:
        """Test metrics have correct namespace prefix from api_title."""
        # Make a request to generate some metrics
        await client.get("/")

        response = await client.get("/metrics")
        content = response.text

        # Get expected prefix from metrics namespace
        expected_prefix = f"{METRIC_NAMESPACE}_http_"

        # Verify metrics with correct prefix exist
        assert f"{expected_prefix}requests_total" in content
        assert f"{expected_prefix}request_duration_highr_seconds" in content
        assert f"{expected_prefix}request_size_bytes" in content
        assert f"{expected_prefix}response_size_bytes" in content

    @pytest.mark.asyncio
    async def test_metrics_endpoint_not_tracked(self, client) -> None:
        """Test that /metrics endpoint itself is excluded from tracking."""
        # Make several requests to /metrics
        for _ in range(5):
            await client.get("/metrics")

        response = await client.get("/metrics")
        content = response.text

        # Check that /metrics is NOT present as a handler in any metric
        # The metrics should not contain handler="/metrics"
        lines = content.split("\n")
        for line in lines:
            if line.startswith("#") or not line.strip():
                continue
            # Skip if this is a metric definition line (starts with # TYPE etc)
            if "handler=" in line:
                assert 'handler="/metrics"' not in line, (
                    "/metrics endpoint should be excluded from tracking"
                )

    @pytest.mark.asyncio
    async def test_heartbeat_endpoint_not_tracked(self, client) -> None:
        """Test that /heartbeat endpoint is excluded from tracking."""
        # Make request to heartbeat
        await client.get("/heartbeat")

        response = await client.get("/metrics")
        content = response.text

        # Check that /heartbeat is NOT present as a handler in any metric
        lines = content.split("\n")
        for line in lines:
            if line.startswith("#") or not line.strip():
                continue
            if "handler=" in line:
                assert 'handler="/heartbeat"' not in line, (
                    "/heartbeat endpoint should be excluded from tracking"
                )

    @pytest.mark.asyncio
    async def test_inprogress_gauge_exists(self, client) -> None:
        """Test that the in-progress requests gauge metric exists."""
        response = await client.get("/metrics")
        content = response.text

        inprogress_metric = f"{METRIC_NAMESPACE}_http_requests_inprogress"

        # Check for TYPE declaration
        assert f"# TYPE {inprogress_metric} gauge" in content
        # Check for HELP text
        assert f"# HELP {inprogress_metric}" in content

    @pytest.mark.asyncio
    async def test_custom_latency_buckets(self, client) -> None:
        """Test that custom latency buckets are present."""
        # Make a request to generate latency metrics
        await client.get("/")

        response = await client.get("/metrics")
        content = response.text

        expected_prefix = f"{METRIC_NAMESPACE}_http_"
        latency_metric = f"{expected_prefix}request_duration_highr_seconds"

        # Custom buckets: 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0
        custom_buckets = [
            "0.01",
            "0.025",
            "0.05",
            "0.1",
            "0.25",
            "0.5",
            "1.0",
            "2.5",
            "5.0",
            "10.0",
        ]

        for bucket in custom_buckets:
            # Look for bucket in histogram
            assert f"{latency_metric}_bucket{{" in content, (
                "Latency histogram should exist"
            )
            assert f'le="{bucket}"' in content, (
                f"Custom bucket {bucket} should be present in latency histogram"
            )

    @pytest.mark.asyncio
    async def test_standard_http_metrics_exist(self, client) -> None:
        """Test that all standard HTTP metrics exist."""
        # Make a request to generate metrics
        await client.get("/")

        response = await client.get("/metrics")
        content = response.text

        expected_prefix = f"{METRIC_NAMESPACE}_http_"

        # Check for all expected metric types
        expected_metrics = [
            f"{expected_prefix}requests_total",
            f"{expected_prefix}request_duration_highr_seconds",
            f"{expected_prefix}request_duration_seconds",
            f"{expected_prefix}request_size_bytes",
            f"{expected_prefix}response_size_bytes",
            f"{expected_prefix}requests_inprogress",
        ]

        for metric in expected_metrics:
            assert metric in content, f"Metric {metric} should be present"

    @pytest.mark.asyncio
    async def test_metrics_track_different_endpoints(self, client) -> None:
        """Test that metrics correctly track different endpoints."""
        # Make requests to different endpoints
        await client.get("/")
        await client.get("/heartbeat")  # Should be excluded
        await client.get("/nonexistent")  # 404

        response = await client.get("/metrics")
        content = response.text

        # Root should be tracked
        assert 'handler="/"' in content

        # Heartbeat should NOT be tracked
        assert 'handler="/heartbeat"' not in content

        # 404s might be grouped or tracked separately depending on config
        # Just verify we got some metrics
        assert "requests_total" in content

    @pytest.mark.asyncio
    async def test_metrics_include_status_codes(self, client) -> None:
        """Test that metrics include HTTP status code labels."""
        # Make successful request
        await client.get("/")

        response = await client.get("/metrics")
        content = response.text

        # Should see status="2xx" for grouped status codes
        assert 'status="2' in content

    @pytest.mark.asyncio
    async def test_metrics_include_method_labels(self, client) -> None:
        """Test that metrics include HTTP method labels."""
        await client.get("/")

        response = await client.get("/metrics")
        content = response.text

        # Should see method="GET"
        assert 'method="GET"' in content

    @pytest.mark.asyncio
    async def test_business_metrics_appear_in_output(self, client) -> None:
        """Test that custom business metrics appear in /metrics output."""
        response = await client.get("/metrics")
        content = response.text

        # Check that all business metric types are defined
        assert (
            f"# TYPE {METRIC_NAMESPACE}_auth_failures_total counter" in content
        )
        assert (
            f"# TYPE {METRIC_NAMESPACE}_api_key_validations_total counter"
            in content
        )
        assert (
            f"# TYPE {METRIC_NAMESPACE}_login_attempts_total counter" in content
        )

        # Check for HELP text
        assert f"# HELP {METRIC_NAMESPACE}_auth_failures_total" in content
        assert f"# HELP {METRIC_NAMESPACE}_api_key_validations_total" in content
        assert f"# HELP {METRIC_NAMESPACE}_login_attempts_total" in content

    @pytest.mark.asyncio
    async def test_login_attempt_metrics(self, client, test_db) -> None:
        """Test that login attempts are tracked correctly."""
        # Create verified test user
        test_db.add(User(**self.test_user))
        await test_db.commit()

        # Get initial metric value
        response = await client.get("/metrics")
        initial_content = response.text

        # Extract initial success count
        initial_success = self._extract_metric_value(
            initial_content,
            f'{METRIC_NAMESPACE}_login_attempts_total{{status="success"}}',
        )

        # Successful login
        login_response = await client.post(
            "/login/",
            json={
                "email": self.test_user["email"],
                "password": self.test_password,
            },
        )
        assert login_response.status_code == status.HTTP_200_OK

        # Check metrics updated
        response = await client.get("/metrics")
        content = response.text

        # Should have incremented by 1
        new_success = self._extract_metric_value(
            content,
            f'{METRIC_NAMESPACE}_login_attempts_total{{status="success"}}',
        )
        assert new_success == initial_success + 1

    @pytest.mark.asyncio
    async def test_login_failure_metrics(self, client, test_db) -> None:
        """Test that failed login attempts are tracked correctly."""
        # Create verified test user
        test_db.add(User(**self.test_user))
        await test_db.commit()

        # Get initial metric value
        response = await client.get("/metrics")
        initial_content = response.text

        initial_invalid = self._extract_metric_value(
            initial_content,
            f'{METRIC_NAMESPACE}_login_attempts_total{{status="invalid_password"}}',
        )

        # Failed login with wrong password
        login_response = await client.post(
            "/login/",
            json={
                "email": self.test_user["email"],
                "password": "wrongpassword123",
            },
        )
        assert login_response.status_code == status.HTTP_400_BAD_REQUEST

        # Check metrics updated
        response = await client.get("/metrics")
        content = response.text

        # Should have incremented by 1
        new_invalid = self._extract_metric_value(
            content,
            f'{METRIC_NAMESPACE}_login_attempts_total{{status="invalid_password"}}',
        )
        assert new_invalid == initial_invalid + 1

    @pytest.mark.asyncio
    async def test_api_key_validation_metrics(self, client) -> None:
        """Test that API key validations are tracked correctly."""
        # Get initial metric value
        response = await client.get("/metrics")
        initial_content = response.text

        initial_invalid_format = self._extract_metric_value(
            initial_content,
            f'{METRIC_NAMESPACE}_api_key_validations_total{{status="invalid_format"}}',
        )

        # Try request with invalid API key format (no prefix)
        await client.get(
            "/users/me", headers={"X-API-Key": "invalid_key_no_prefix"}
        )

        # Check metrics updated
        response = await client.get("/metrics")
        content = response.text

        # Should have incremented by 1
        new_invalid_format = self._extract_metric_value(
            content,
            f'{METRIC_NAMESPACE}_api_key_validations_total{{status="invalid_format"}}',
        )
        assert new_invalid_format == initial_invalid_format + 1

    @pytest.mark.asyncio
    async def test_auth_failure_metrics(self, client) -> None:
        """Test that auth failures are tracked correctly."""
        # Get initial metric value
        response = await client.get("/metrics")
        initial_content = response.text

        initial_invalid = self._extract_metric_value(
            initial_content,
            f'{METRIC_NAMESPACE}_auth_failures_total{{method="jwt",reason="invalid_token"}}',
        )

        # Try request with invalid token
        await client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        # Check metrics updated
        response = await client.get("/metrics")
        content = response.text

        # Should have incremented by 1
        new_invalid = self._extract_metric_value(
            content,
            f'{METRIC_NAMESPACE}_auth_failures_total{{method="jwt",reason="invalid_token"}}',
        )
        assert new_invalid == initial_invalid + 1
