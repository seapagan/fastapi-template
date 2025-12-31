"""Unit tests for the Prometheus instrumentator module."""

import pytest
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pytest_mock import MockerFixture

from app.metrics.instrumentator import get_instrumentator, register_metrics
from app.metrics.namespace import METRIC_NAMESPACE


@pytest.mark.unit
class TestGetInstrumentator:
    """Test the get_instrumentator function."""

    def test_returns_instrumentator_instance(self) -> None:
        """Test that function returns an Instrumentator instance."""
        result = get_instrumentator()

        assert isinstance(result, Instrumentator)

    def test_configures_in_progress_requests(
        self, mocker: MockerFixture
    ) -> None:
        """Test that in-progress request tracking is enabled."""
        mock_instrumentator = mocker.patch(
            "app.metrics.instrumentator.Instrumentator"
        )

        get_instrumentator()

        # Verify Instrumentator was called with correct arguments
        mock_instrumentator.assert_called_once_with(
            should_instrument_requests_inprogress=True,
            inprogress_labels=True,
            inprogress_name=f"{METRIC_NAMESPACE}_http_requests_inprogress",
            excluded_handlers=[r"/metrics", r".*heartbeat.*"],
        )

    def test_sets_correct_inprogress_name(self, mocker: MockerFixture) -> None:
        """Test that in-progress metric uses correct namespace."""
        mock_instrumentator = mocker.patch(
            "app.metrics.instrumentator.Instrumentator"
        )

        get_instrumentator()

        call_kwargs = mock_instrumentator.call_args.kwargs
        expected_name = f"{METRIC_NAMESPACE}_http_requests_inprogress"
        assert call_kwargs["inprogress_name"] == expected_name

    def test_excludes_metrics_and_heartbeat_handlers(
        self, mocker: MockerFixture
    ) -> None:
        """Test that /metrics and /heartbeat endpoints are excluded."""
        mock_instrumentator = mocker.patch(
            "app.metrics.instrumentator.Instrumentator"
        )

        get_instrumentator()

        call_kwargs = mock_instrumentator.call_args.kwargs
        excluded = call_kwargs["excluded_handlers"]
        assert r"/metrics" in excluded
        assert r".*heartbeat.*" in excluded

    def test_enables_inprogress_labels(self, mocker: MockerFixture) -> None:
        """Test that inprogress_labels is enabled."""
        mock_instrumentator = mocker.patch(
            "app.metrics.instrumentator.Instrumentator"
        )

        get_instrumentator()

        call_kwargs = mock_instrumentator.call_args.kwargs
        assert call_kwargs["inprogress_labels"] is True


@pytest.mark.unit
class TestRegisterMetrics:
    """Test the register_metrics function."""

    def test_does_nothing_when_metrics_disabled(
        self, mocker: MockerFixture
    ) -> None:
        """Test that no instrumentation occurs when metrics are disabled."""
        # Mock settings to disable metrics
        mock_settings = mocker.patch("app.metrics.instrumentator.get_settings")
        mock_settings.return_value.metrics_enabled = False

        # Mock get_instrumentator to track if it's called
        mock_get_instrumentator = mocker.patch(
            "app.metrics.instrumentator.get_instrumentator"
        )

        app = FastAPI()
        register_metrics(app)

        # Verify get_instrumentator was not called
        mock_get_instrumentator.assert_not_called()

    def test_registers_metrics_when_enabled(
        self, mocker: MockerFixture
    ) -> None:
        """Test that instrumentation occurs when metrics are enabled."""
        # Mock settings to enable metrics
        mock_settings = mocker.patch("app.metrics.instrumentator.get_settings")
        mock_settings.return_value.metrics_enabled = True
        mock_settings.return_value.api_title = "API Template"

        # Mock the instrumentator chain
        mock_instrumentator = mocker.MagicMock()
        mock_instrument = mocker.MagicMock()
        mock_instrumentator.instrument.return_value = mock_instrument

        mock_get_instrumentator = mocker.patch(
            "app.metrics.instrumentator.get_instrumentator"
        )
        mock_get_instrumentator.return_value = mock_instrumentator

        app = FastAPI()
        register_metrics(app)

        # Verify instrument was called
        mock_instrumentator.instrument.assert_called_once()
        # Verify expose was called on the result of instrument
        mock_instrument.expose.assert_called_once_with(app)

    def test_applies_correct_namespace(self, mocker: MockerFixture) -> None:
        """Test that metric namespace is derived from api_title."""
        # Mock settings
        mock_settings = mocker.patch("app.metrics.instrumentator.get_settings")
        mock_settings.return_value.metrics_enabled = True
        mock_settings.return_value.api_title = "My API Service"

        # Mock the instrumentator chain
        mock_instrumentator = mocker.MagicMock()
        mock_instrument = mocker.MagicMock()
        mock_instrumentator.instrument.return_value = mock_instrument

        mock_get_instrumentator = mocker.patch(
            "app.metrics.instrumentator.get_instrumentator"
        )
        mock_get_instrumentator.return_value = mock_instrumentator

        app = FastAPI()
        register_metrics(app)

        # Verify namespace was correctly transformed
        call_kwargs = mock_instrumentator.instrument.call_args.kwargs
        assert call_kwargs["metric_namespace"] == "my_api_service"

    def test_applies_custom_latency_buckets(
        self, mocker: MockerFixture
    ) -> None:
        """Test that custom latency buckets are applied."""
        # Mock settings
        mock_settings = mocker.patch("app.metrics.instrumentator.get_settings")
        mock_settings.return_value.metrics_enabled = True
        mock_settings.return_value.api_title = "API Template"

        # Mock the instrumentator chain
        mock_instrumentator = mocker.MagicMock()
        mock_instrument = mocker.MagicMock()
        mock_instrumentator.instrument.return_value = mock_instrument

        mock_get_instrumentator = mocker.patch(
            "app.metrics.instrumentator.get_instrumentator"
        )
        mock_get_instrumentator.return_value = mock_instrumentator

        app = FastAPI()
        register_metrics(app)

        # Verify latency buckets
        call_kwargs = mock_instrumentator.instrument.call_args.kwargs
        expected_buckets = (
            0.01,
            0.025,
            0.05,
            0.1,
            0.25,
            0.5,
            1.0,
            2.5,
            5.0,
            10.0,
        )
        assert call_kwargs["latency_highr_buckets"] == expected_buckets

    def test_calls_expose_on_app(self, mocker: MockerFixture) -> None:
        """Test that expose is called with the FastAPI app instance."""
        # Mock settings
        mock_settings = mocker.patch("app.metrics.instrumentator.get_settings")
        mock_settings.return_value.metrics_enabled = True
        mock_settings.return_value.api_title = "API Template"

        # Mock the instrumentator chain
        mock_instrumentator = mocker.MagicMock()
        mock_instrument = mocker.MagicMock()
        mock_instrumentator.instrument.return_value = mock_instrument

        mock_get_instrumentator = mocker.patch(
            "app.metrics.instrumentator.get_instrumentator"
        )
        mock_get_instrumentator.return_value = mock_instrumentator

        app = FastAPI()
        register_metrics(app)

        # Verify expose was called with the app
        mock_instrument.expose.assert_called_once_with(app)
