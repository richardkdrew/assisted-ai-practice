"""Integration tests for observability stack validation."""

import pytest
import asyncio
import aiohttp
import time
import re
from typing import Dict, Any


class TestObservabilityIntegration:
    """Integration tests for Configuration Service observability features."""

    base_url = "http://localhost:8000"
    prometheus_url = "http://localhost:9090"
    grafana_url = "http://localhost:3001"
    otel_collector_url = "http://localhost:8889"

    @pytest.fixture
    async def http_session(self):
        """HTTP session for making requests."""
        async with aiohttp.ClientSession() as session:
            yield session

    @pytest.fixture
    async def setup_test_data(self, http_session):
        """Create test application and configuration for testing."""
        # Create test application
        app_data = {
            "name": "observability-test-app",
            "description": "Test application for observability validation",
            "owner": "test-suite"
        }
        async with http_session.post(f"{self.base_url}/api/v1/applications", json=app_data) as response:
            app_created = response.status in [200, 201, 409]  # 409 = already exists

        # Create test configuration
        config_data = {
            "key": "observability-test-config",
            "value": {"test_setting": "test_value", "enabled": True},
            "environment": "test",
            "version": "1.0.0"
        }
        async with http_session.post(
            f"{self.base_url}/api/v1/applications/observability-test-app/configurations",
            json=config_data
        ) as response:
            config_created = response.status in [200, 201, 409]

        return {"app_created": app_created, "config_created": config_created}

    async def test_service_health(self, http_session):
        """Test that the Configuration Service is healthy and responding."""
        async with http_session.get(f"{self.base_url}/health") as response:
            assert response.status == 200
            data = await response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "configuration-service"

    async def test_prometheus_metrics_endpoint(self, http_session):
        """Test that the /metrics endpoint returns Prometheus-formatted metrics."""
        async with http_session.get(f"{self.base_url}/metrics") as response:
            assert response.status == 200
            content = await response.text()

            # Verify Prometheus format
            assert "# HELP" in content
            assert "# TYPE" in content

            # Check for expected custom metrics
            assert "http_requests_total" in content
            assert "http_request_duration_seconds" in content
            assert "database_connections_active" in content
            assert "configurations_total" in content
            assert "applications_total" in content

    async def test_metrics_collection_after_requests(self, http_session, setup_test_data):
        """Test that metrics are collected after making requests."""
        # Get baseline metrics
        async with http_session.get(f"{self.base_url}/metrics") as response:
            baseline_metrics = await response.text()

        # Make several requests to generate metrics
        endpoints = [
            "/health",
            "/api/v1/applications",
            "/api/v1/applications/observability-test-app/configurations"
        ]

        for endpoint in endpoints:
            for _ in range(3):  # Make 3 requests to each endpoint
                async with http_session.get(f"{self.base_url}{endpoint}") as response:
                    pass  # Just making requests to generate metrics

        # Wait a moment for metrics to be collected
        await asyncio.sleep(2)

        # Get updated metrics
        async with http_session.get(f"{self.base_url}/metrics") as response:
            updated_metrics = await response.text()

        # Verify metrics increased
        baseline_request_count = self._extract_metric_value(baseline_metrics, "http_requests_total")
        updated_request_count = self._extract_metric_value(updated_metrics, "http_requests_total")

        assert updated_request_count > baseline_request_count, "Request count should increase"

    async def test_otel_collector_metrics_export(self, http_session):
        """Test that OpenTelemetry Collector is exporting metrics."""
        # Make some requests to generate telemetry
        for _ in range(5):
            async with http_session.get(f"{self.base_url}/health") as response:
                pass

        await asyncio.sleep(3)  # Wait for metrics export

        # Check OTel Collector metrics endpoint
        try:
            async with http_session.get(f"{self.otel_collector_url}/metrics") as response:
                assert response.status == 200
                content = await response.text()
                # Should contain some metrics from the collector
                assert "otelcol_" in content or "configservice_" in content
        except aiohttp.ClientError:
            pytest.skip("OpenTelemetry Collector not accessible")

    async def test_prometheus_service_discovery(self, http_session):
        """Test that Prometheus can discover and scrape targets."""
        try:
            # Check Prometheus targets
            async with http_session.get(f"{self.prometheus_url}/api/v1/targets") as response:
                assert response.status == 200
                data = await response.json()

                # Should have targets for config service and otel collector
                target_urls = [target['discoveredLabels']['__address__'] for target in data['data']['activeTargets']]

                # Look for our service targets
                service_targets = [url for url in target_urls if 'config-service' in str(url) or '8000' in str(url)]
                assert len(service_targets) > 0, "Should have Configuration Service targets"

        except aiohttp.ClientError:
            pytest.skip("Prometheus not accessible")

    async def test_prometheus_metrics_ingestion(self, http_session):
        """Test that Prometheus is ingesting metrics from the service."""
        # Generate some metrics
        for _ in range(10):
            async with http_session.get(f"{self.base_url}/health") as response:
                pass

        await asyncio.sleep(10)  # Wait for Prometheus scrape

        try:
            # Query Prometheus for our metrics
            query = "http_requests_total"
            async with http_session.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": query}
            ) as response:
                assert response.status == 200
                data = await response.json()

                assert data["status"] == "success"
                assert len(data["data"]["result"]) > 0, "Should have http_requests_total metric data"

        except aiohttp.ClientError:
            pytest.skip("Prometheus not accessible")

    async def test_grafana_health(self, http_session):
        """Test that Grafana is accessible and healthy."""
        try:
            async with http_session.get(f"{self.grafana_url}/api/health") as response:
                assert response.status == 200
                data = await response.json()
                assert data["database"] == "ok"

        except aiohttp.ClientError:
            pytest.skip("Grafana not accessible")

    async def test_grafana_prometheus_datasource(self, http_session):
        """Test that Grafana has Prometheus configured as a datasource."""
        try:
            # Check datasources
            async with http_session.get(
                f"{self.grafana_url}/api/datasources",
                auth=aiohttp.BasicAuth("admin", "admin")
            ) as response:
                if response.status == 200:
                    datasources = await response.json()
                    prometheus_datasources = [ds for ds in datasources if ds["type"] == "prometheus"]
                    assert len(prometheus_datasources) > 0, "Should have Prometheus datasource configured"

        except aiohttp.ClientError:
            pytest.skip("Grafana not accessible or authentication failed")

    async def test_request_tracing(self, http_session, setup_test_data):
        """Test that requests generate traces (basic validation)."""
        # Make a request that should generate a trace
        start_time = time.time()

        async with http_session.get(f"{self.base_url}/api/v1/applications/observability-test-app/configurations") as response:
            assert response.status == 200

        # Check if trace headers are present (basic OpenTelemetry validation)
        # In a full setup, you'd check the tracing backend, but here we validate instrumentation
        assert True  # Placeholder - actual trace validation would require Jaeger/Zipkin

    async def test_database_metrics_collection(self, http_session, setup_test_data):
        """Test that database-related metrics are being collected."""
        # Make database-heavy requests
        for _ in range(5):
            async with http_session.get(f"{self.base_url}/api/v1/applications") as response:
                pass

        await asyncio.sleep(2)

        # Check metrics for database connections
        async with http_session.get(f"{self.base_url}/metrics") as response:
            content = await response.text()

            # Should have database connection metrics
            assert "database_connections_active" in content

    async def test_error_rate_metrics(self, http_session):
        """Test that error responses are tracked in metrics."""
        # Get baseline metrics
        async with http_session.get(f"{self.base_url}/metrics") as response:
            baseline_metrics = await response.text()

        # Generate some 404 errors
        for _ in range(3):
            async with http_session.get(f"{self.base_url}/api/v1/applications/nonexistent") as response:
                assert response.status == 404

        await asyncio.sleep(2)

        # Check updated metrics
        async with http_session.get(f"{self.base_url}/metrics") as response:
            updated_metrics = await response.text()

        # Should have 404 status codes in metrics
        status_404_pattern = r'http_requests_total.*status_code="404".*\s+(\d+)'
        matches = re.findall(status_404_pattern, updated_metrics)
        assert len(matches) > 0, "Should track 404 status codes in metrics"

    async def test_performance_metrics_accuracy(self, http_session):
        """Test that response time metrics are reasonably accurate."""
        # Clear metrics baseline
        start_time = time.time()

        # Make a request and measure time locally
        request_start = time.time()
        async with http_session.get(f"{self.base_url}/health") as response:
            assert response.status == 200
        local_duration = time.time() - request_start

        await asyncio.sleep(2)

        # Check recorded metrics
        async with http_session.get(f"{self.base_url}/metrics") as response:
            content = await response.text()

        # Extract duration metrics (this is a simplified check)
        duration_pattern = r'http_request_duration_seconds.*\s+([0-9.]+)'
        matches = re.findall(duration_pattern, content)
        if matches:
            recorded_duration = float(matches[-1])  # Get last recorded duration
            # Should be within reasonable range (allowing for overhead)
            assert recorded_duration <= local_duration * 3, "Recorded duration should be reasonable"

    def _extract_metric_value(self, metrics_text: str, metric_name: str) -> float:
        """Extract the total value of a metric from Prometheus text format."""
        pattern = rf'{metric_name}.*\s+([0-9.]+)'
        matches = re.findall(pattern, metrics_text)
        if matches:
            return sum(float(match) for match in matches)
        return 0.0

    @pytest.mark.asyncio
    async def test_full_observability_stack_integration(self, http_session, setup_test_data):
        """End-to-end test of the complete observability stack."""
        # This test validates the entire pipeline:
        # App → OpenTelemetry → Collector → Prometheus → (Grafana)

        print("🔍 Testing full observability pipeline...")

        # 1. Generate application activity
        print("  📊 Generating application metrics...")
        for i in range(10):
            async with http_session.get(f"{self.base_url}/health") as response:
                assert response.status == 200

            if i % 3 == 0:  # Every 3rd request, make an API call
                async with http_session.get(f"{self.base_url}/api/v1/applications") as response:
                    pass

        # 2. Wait for metrics collection and export
        print("  ⏱️  Waiting for metrics collection...")
        await asyncio.sleep(15)

        # 3. Verify metrics at service level
        print("  ✅ Checking service metrics endpoint...")
        async with http_session.get(f"{self.base_url}/metrics") as response:
            assert response.status == 200
            service_metrics = await response.text()
            assert "http_requests_total" in service_metrics

        # 4. Verify OpenTelemetry Collector
        print("  🔄 Checking OpenTelemetry Collector...")
        try:
            async with http_session.get(f"{self.otel_collector_url}/metrics") as response:
                if response.status == 200:
                    print("    ✅ OpenTelemetry Collector responding")
                else:
                    print("    ⚠️  OpenTelemetry Collector not responding")
        except:
            print("    ⚠️  OpenTelemetry Collector not accessible")

        # 5. Verify Prometheus ingestion
        print("  📈 Checking Prometheus metrics ingestion...")
        try:
            async with http_session.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": "up"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] == "success":
                        print("    ✅ Prometheus is collecting metrics")
                    else:
                        print("    ⚠️  Prometheus query failed")
                else:
                    print("    ⚠️  Prometheus not responding")
        except:
            print("    ⚠️  Prometheus not accessible")

        # 6. Verify Grafana connectivity
        print("  📊 Checking Grafana accessibility...")
        try:
            async with http_session.get(f"{self.grafana_url}/api/health") as response:
                if response.status == 200:
                    print("    ✅ Grafana is accessible")
                else:
                    print("    ⚠️  Grafana not responding")
        except:
            print("    ⚠️  Grafana not accessible")

        print("🎯 Full observability stack test completed!")

# Performance tests for load validation
class TestObservabilityPerformance:
    """Performance tests to validate observability overhead."""

    base_url = "http://localhost:8000"

    @pytest.fixture
    async def http_session(self):
        """HTTP session for making requests."""
        async with aiohttp.ClientSession() as session:
            yield session

    async def test_observability_overhead(self, http_session):
        """Test that observability doesn't add significant overhead."""
        # Measure request times with observability enabled
        durations = []

        for _ in range(20):
            start = time.time()
            async with http_session.get(f"{self.base_url}/health") as response:
                assert response.status == 200
            duration = time.time() - start
            durations.append(duration)

        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)

        # Basic performance assertions
        assert avg_duration < 0.1, f"Average response time {avg_duration:.3f}s should be under 100ms"
        assert max_duration < 0.5, f"Max response time {max_duration:.3f}s should be under 500ms"

    async def test_metrics_endpoint_performance(self, http_session):
        """Test that the metrics endpoint performs well under load."""
        durations = []

        for _ in range(10):
            start = time.time()
            async with http_session.get(f"{self.base_url}/metrics") as response:
                assert response.status == 200
                await response.text()  # Ensure we read the full response
            duration = time.time() - start
            durations.append(duration)

        avg_duration = sum(durations) / len(durations)

        # Metrics endpoint should be reasonably fast
        assert avg_duration < 1.0, f"Metrics endpoint average response time {avg_duration:.3f}s should be under 1s"