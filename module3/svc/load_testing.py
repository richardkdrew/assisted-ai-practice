#!/usr/bin/env python3
"""Load testing framework for Configuration Service observability validation."""

import asyncio
import aiohttp
import json
import time
import random
import argparse
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LoadTestResult:
    """Results from a load testing scenario."""
    scenario_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    max_response_time: float
    min_response_time: float
    requests_per_second: float
    duration: float
    error_rates: Dict[str, int]


class ConfigServiceLoadTester:
    """Load tester for Configuration Service."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results: List[LoadTestResult] = []

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def health_check(self) -> bool:
        """Verify service is healthy before testing."""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                return response.status == 200
        except Exception:
            return False

    async def create_test_application(self, app_id: str) -> bool:
        """Create a test application for load testing."""
        app_data = {
            "name": f"load-test-app-{app_id}",
            "description": f"Load testing application {app_id}",
            "owner": "load-tester"
        }
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/applications",
                json=app_data
            ) as response:
                return response.status in [200, 201, 409]  # 409 = already exists
        except Exception:
            return False

    async def create_test_configuration(self, app_id: str, config_id: str) -> bool:
        """Create a test configuration."""
        config_data = {
            "key": f"load-test-config-{config_id}",
            "value": {"setting": f"value-{config_id}", "enabled": True},
            "environment": "load-test",
            "version": "1.0.0"
        }
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/applications/{app_id}/configurations",
                json=config_data
            ) as response:
                return response.status in [200, 201, 409]
        except Exception:
            return False

    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a single HTTP request and measure performance."""
        start_time = time.time()
        try:
            async with self.session.request(method, f"{self.base_url}{endpoint}", **kwargs) as response:
                end_time = time.time()
                return {
                    "success": True,
                    "status_code": response.status,
                    "response_time": end_time - start_time,
                    "error": None
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "status_code": 0,
                "response_time": end_time - start_time,
                "error": str(e)
            }

    async def scenario_health_check_stress(self, duration: int = 60, rps: int = 50) -> LoadTestResult:
        """Stress test the health check endpoint."""
        print(f"Running health check stress test: {rps} RPS for {duration}s")

        start_time = time.time()
        end_time = start_time + duration
        results = []
        error_counts = {}

        while time.time() < end_time:
            batch_size = min(rps, int((end_time - time.time()) * rps))
            if batch_size <= 0:
                break

            tasks = [
                self.make_request("GET", "/health")
                for _ in range(batch_size)
            ]

            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            # Count errors
            for result in batch_results:
                if not result["success"]:
                    error_type = result["error"] or f"HTTP_{result['status_code']}"
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1

            await asyncio.sleep(1)  # Wait 1 second between batches

        return self._calculate_results("Health Check Stress", results, error_counts, time.time() - start_time)

    async def scenario_api_mixed_load(self, duration: int = 120, rps: int = 20) -> LoadTestResult:
        """Mixed load test with various API operations."""
        print(f"Running mixed API load test: {rps} RPS for {duration}s")

        # Setup test data
        test_app_id = "load-test-app"
        await self.create_test_application(test_app_id)
        for i in range(5):
            await self.create_test_configuration(test_app_id, f"config-{i}")

        start_time = time.time()
        end_time = start_time + duration
        results = []
        error_counts = {}

        while time.time() < end_time:
            batch_size = min(rps, int((end_time - time.time()) * rps))
            if batch_size <= 0:
                break

            # Mix of operations: 40% reads, 30% writes, 20% lists, 10% health
            tasks = []
            for _ in range(batch_size):
                operation = random.choices(
                    ["read", "write", "list", "health"],
                    weights=[40, 30, 20, 10]
                )[0]

                if operation == "read":
                    config_id = f"config-{random.randint(0, 4)}"
                    tasks.append(self.make_request(
                        "GET",
                        f"/api/v1/applications/{test_app_id}/configurations/{config_id}"
                    ))
                elif operation == "write":
                    config_id = f"config-{random.randint(0, 9)}"
                    tasks.append(self.make_request(
                        "POST",
                        f"/api/v1/applications/{test_app_id}/configurations",
                        json={
                            "key": f"load-config-{config_id}",
                            "value": {"setting": f"value-{random.randint(1, 1000)}"},
                            "environment": "load-test",
                            "version": "1.0.0"
                        }
                    ))
                elif operation == "list":
                    tasks.append(self.make_request("GET", f"/api/v1/applications/{test_app_id}/configurations"))
                else:  # health
                    tasks.append(self.make_request("GET", "/health"))

            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            # Count errors
            for result in batch_results:
                if not result["success"]:
                    error_type = result["error"] or f"HTTP_{result['status_code']}"
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1

            await asyncio.sleep(1)

        return self._calculate_results("Mixed API Load", results, error_counts, time.time() - start_time)

    async def scenario_metrics_endpoint_load(self, duration: int = 30, rps: int = 10) -> LoadTestResult:
        """Load test the Prometheus metrics endpoint."""
        print(f"Running metrics endpoint load test: {rps} RPS for {duration}s")

        start_time = time.time()
        end_time = start_time + duration
        results = []
        error_counts = {}

        while time.time() < end_time:
            batch_size = min(rps, int((end_time - time.time()) * rps))
            if batch_size <= 0:
                break

            tasks = [
                self.make_request("GET", "/metrics")
                for _ in range(batch_size)
            ]

            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            for result in batch_results:
                if not result["success"]:
                    error_type = result["error"] or f"HTTP_{result['status_code']}"
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1

            await asyncio.sleep(1)

        return self._calculate_results("Metrics Endpoint Load", results, error_counts, time.time() - start_time)

    async def scenario_spike_test(self, base_rps: int = 10, spike_rps: int = 100, spike_duration: int = 30) -> LoadTestResult:
        """Spike test with sudden load increase."""
        print(f"Running spike test: {base_rps} RPS → {spike_rps} RPS for {spike_duration}s")

        start_time = time.time()
        results = []
        error_counts = {}

        # Base load for 30 seconds
        base_end = start_time + 30
        while time.time() < base_end:
            tasks = [self.make_request("GET", "/health") for _ in range(base_rps)]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            await asyncio.sleep(1)

        # Spike load
        spike_end = time.time() + spike_duration
        while time.time() < spike_end:
            tasks = [self.make_request("GET", "/health") for _ in range(spike_rps)]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            for result in batch_results:
                if not result["success"]:
                    error_type = result["error"] or f"HTTP_{result['status_code']}"
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1

            await asyncio.sleep(1)

        # Return to base load for 30 seconds
        base_end = time.time() + 30
        while time.time() < base_end:
            tasks = [self.make_request("GET", "/health") for _ in range(base_rps)]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            await asyncio.sleep(1)

        return self._calculate_results("Spike Test", results, error_counts, time.time() - start_time)

    def _calculate_results(self, scenario_name: str, results: List[Dict], error_counts: Dict, duration: float) -> LoadTestResult:
        """Calculate load test results."""
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = total_requests - successful_requests

        response_times = [r["response_time"] for r in results]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0

        rps = total_requests / duration if duration > 0 else 0

        return LoadTestResult(
            scenario_name=scenario_name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=avg_response_time,
            max_response_time=max_response_time,
            min_response_time=min_response_time,
            requests_per_second=rps,
            duration=duration,
            error_rates=error_counts
        )

    async def run_all_scenarios(self) -> List[LoadTestResult]:
        """Run all load testing scenarios."""
        print("Starting Configuration Service load testing...")
        print(f"Target URL: {self.base_url}")
        print(f"Test start time: {datetime.now()}")

        # Health check
        if not await self.health_check():
            print("❌ Service health check failed. Ensure the service is running.")
            return []

        print("✅ Service health check passed")

        # Run scenarios
        scenarios = [
            self.scenario_health_check_stress(duration=60, rps=50),
            self.scenario_api_mixed_load(duration=120, rps=20),
            self.scenario_metrics_endpoint_load(duration=30, rps=10),
            self.scenario_spike_test(base_rps=10, spike_rps=100, spike_duration=30)
        ]

        results = []
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n--- Scenario {i}/{len(scenarios)} ---")
            result = await scenario
            results.append(result)
            self._print_result(result)

            # Brief pause between scenarios
            if i < len(scenarios):
                print("Pausing 10 seconds before next scenario...")
                await asyncio.sleep(10)

        return results

    def _print_result(self, result: LoadTestResult):
        """Print load test results."""
        print(f"\n📊 {result.scenario_name} Results:")
        print(f"   Duration: {result.duration:.2f}s")
        print(f"   Total Requests: {result.total_requests}")
        print(f"   Successful: {result.successful_requests} ({result.successful_requests/result.total_requests*100:.1f}%)")
        print(f"   Failed: {result.failed_requests} ({result.failed_requests/result.total_requests*100:.1f}%)")
        print(f"   Requests/Second: {result.requests_per_second:.2f}")
        print(f"   Avg Response Time: {result.average_response_time*1000:.2f}ms")
        print(f"   Min Response Time: {result.min_response_time*1000:.2f}ms")
        print(f"   Max Response Time: {result.max_response_time*1000:.2f}ms")

        if result.error_rates:
            print(f"   Error Breakdown:")
            for error_type, count in result.error_rates.items():
                print(f"     {error_type}: {count}")

    def generate_report(self, results: List[LoadTestResult]) -> str:
        """Generate a comprehensive load testing report."""
        report = []
        report.append("# Configuration Service Load Testing Report")
        report.append(f"\nGenerated: {datetime.now()}")
        report.append(f"Target Service: {self.base_url}")
        report.append("\n## Summary")

        total_requests = sum(r.total_requests for r in results)
        total_successful = sum(r.successful_requests for r in results)
        total_failed = sum(r.failed_requests for r in results)
        overall_success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0

        report.append(f"- Total Requests: {total_requests}")
        report.append(f"- Success Rate: {overall_success_rate:.2f}%")
        report.append(f"- Total Duration: {sum(r.duration for r in results):.2f}s")

        report.append("\n## Scenario Details")
        for result in results:
            report.append(f"\n### {result.scenario_name}")
            report.append(f"- Duration: {result.duration:.2f}s")
            report.append(f"- Requests: {result.total_requests}")
            report.append(f"- Success Rate: {result.successful_requests/result.total_requests*100:.2f}%")
            report.append(f"- RPS: {result.requests_per_second:.2f}")
            report.append(f"- Avg Response Time: {result.average_response_time*1000:.2f}ms")

        report.append("\n## Observability Validation")
        report.append("During load testing, verify the following metrics are captured:")
        report.append("- [ ] HTTP request counts by endpoint and status code")
        report.append("- [ ] HTTP request duration histograms")
        report.append("- [ ] Database connection pool metrics")
        report.append("- [ ] Application-specific business metrics")
        report.append("- [ ] Container resource utilization (CPU, memory, network)")
        report.append("- [ ] OpenTelemetry trace spans for request flows")

        return "\n".join(report)


async def main():
    """Main entry point for load testing."""
    parser = argparse.ArgumentParser(description="Configuration Service Load Tester")
    parser.add_argument("--url", default="http://localhost:8000", help="Service base URL")
    parser.add_argument("--report", help="Save report to file")
    args = parser.parse_args()

    async with ConfigServiceLoadTester(args.url) as tester:
        results = await tester.run_all_scenarios()

        if results:
            print("\n" + "="*60)
            print("🎯 LOAD TESTING COMPLETE")
            print("="*60)

            report = tester.generate_report(results)
            print(report)

            if args.report:
                with open(args.report, 'w') as f:
                    f.write(report)
                print(f"\n📄 Report saved to: {args.report}")
        else:
            print("❌ Load testing failed to complete")


if __name__ == "__main__":
    asyncio.run(main())