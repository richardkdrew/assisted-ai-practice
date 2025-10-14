"""Tests for retry strategy."""

import asyncio

import httpx
import pytest

from detective_agent.retry.strategy import (
    RetryConfig,
    is_retryable_error,
    with_retry,
)


class TestIsRetryableError:
    """Tests for error classification."""

    def test_rate_limit_error_is_retryable(self):
        """Test that 429 rate limit errors are retryable."""
        response = httpx.Response(429, request=httpx.Request("GET", "http://test.com"))
        error = httpx.HTTPStatusError("", request=response.request, response=response)
        assert is_retryable_error(error) is True

    def test_server_errors_are_retryable(self):
        """Test that 500, 502, 503 errors are retryable."""
        for status_code in [500, 502, 503, 504]:
            response = httpx.Response(
                status_code, request=httpx.Request("GET", "http://test.com")
            )
            error = httpx.HTTPStatusError("", request=response.request, response=response)
            assert is_retryable_error(error) is True

    def test_auth_errors_are_not_retryable(self):
        """Test that 401 and 403 errors are not retryable."""
        for status_code in [401, 403]:
            response = httpx.Response(
                status_code, request=httpx.Request("GET", "http://test.com")
            )
            error = httpx.HTTPStatusError("", request=response.request, response=response)
            assert is_retryable_error(error) is False

    def test_bad_request_is_not_retryable(self):
        """Test that 400 bad request is not retryable."""
        response = httpx.Response(400, request=httpx.Request("GET", "http://test.com"))
        error = httpx.HTTPStatusError("", request=response.request, response=response)
        assert is_retryable_error(error) is False

    def test_not_found_is_not_retryable(self):
        """Test that 404 not found is not retryable."""
        response = httpx.Response(404, request=httpx.Request("GET", "http://test.com"))
        error = httpx.HTTPStatusError("", request=response.request, response=response)
        assert is_retryable_error(error) is False

    def test_timeout_is_retryable(self):
        """Test that timeout errors are retryable."""
        error = httpx.TimeoutException("")
        assert is_retryable_error(error) is True

    def test_network_error_is_retryable(self):
        """Test that network errors are retryable."""
        error = httpx.NetworkError("")
        assert is_retryable_error(error) is True

    def test_connect_error_is_retryable(self):
        """Test that connect errors are retryable."""
        error = httpx.ConnectError("")
        assert is_retryable_error(error) is True

    def test_unknown_error_is_not_retryable(self):
        """Test that unknown errors are not retryable by default."""
        error = ValueError("Unknown error")
        assert is_retryable_error(error) is False


class TestWithRetry:
    """Tests for retry mechanism."""

    @pytest.mark.asyncio
    async def test_successful_operation_no_retry(self):
        """Test that successful operations don't trigger retries."""
        call_count = 0

        async def success_operation():
            nonlocal call_count
            call_count += 1
            return "success"

        config = RetryConfig(max_attempts=3)
        result = await with_retry(success_operation, config, "test_operation")

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retryable_error_triggers_retry(self):
        """Test that retryable errors trigger retries."""
        call_count = 0

        async def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                response = httpx.Response(
                    429, request=httpx.Request("GET", "http://test.com")
                )
                raise httpx.HTTPStatusError("", request=response.request, response=response)
            return "success"

        config = RetryConfig(max_attempts=3, initial_delay=0.01)
        result = await with_retry(failing_then_success, config, "test_operation")

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_non_retryable_error_fails_fast(self):
        """Test that non-retryable errors fail immediately."""
        call_count = 0

        async def auth_error():
            nonlocal call_count
            call_count += 1
            response = httpx.Response(401, request=httpx.Request("GET", "http://test.com"))
            raise httpx.HTTPStatusError("", request=response.request, response=response)

        config = RetryConfig(max_attempts=3)

        with pytest.raises(httpx.HTTPStatusError):
            await with_retry(auth_error, config, "test_operation")

        assert call_count == 1  # Only called once, no retries

    @pytest.mark.asyncio
    async def test_max_retries_exhausted(self):
        """Test that operation fails after max retries."""
        call_count = 0

        async def always_fails():
            nonlocal call_count
            call_count += 1
            response = httpx.Response(500, request=httpx.Request("GET", "http://test.com"))
            raise httpx.HTTPStatusError("", request=response.request, response=response)

        config = RetryConfig(max_attempts=3, initial_delay=0.01)

        with pytest.raises(httpx.HTTPStatusError):
            await with_retry(always_fails, config, "test_operation")

        assert call_count == 3  # Called max_attempts times

    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test that backoff increases exponentially."""
        call_times = []

        async def failing_operation():
            call_times.append(asyncio.get_event_loop().time())
            response = httpx.Response(500, request=httpx.Request("GET", "http://test.com"))
            raise httpx.HTTPStatusError("", request=response.request, response=response)

        config = RetryConfig(
            max_attempts=3, initial_delay=0.1, backoff_factor=2.0, jitter=False
        )

        with pytest.raises(httpx.HTTPStatusError):
            await with_retry(failing_operation, config, "test_operation")

        # Check that delays increase (approximately)
        # First attempt: immediate
        # Second attempt: ~0.1s delay
        # Third attempt: ~0.2s delay
        assert len(call_times) == 3
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]

        # Allow some tolerance for timing
        assert 0.08 < delay1 < 0.15
        assert 0.18 < delay2 < 0.25

    @pytest.mark.asyncio
    async def test_max_delay_cap(self):
        """Test that backoff doesn't exceed max_delay."""
        call_times = []

        async def failing_operation():
            call_times.append(asyncio.get_event_loop().time())
            response = httpx.Response(500, request=httpx.Request("GET", "http://test.com"))
            raise httpx.HTTPStatusError("", request=response.request, response=response)

        config = RetryConfig(
            max_attempts=4,
            initial_delay=1.0,
            backoff_factor=10.0,
            max_delay=0.5,
            jitter=False,
        )

        with pytest.raises(httpx.HTTPStatusError):
            await with_retry(failing_operation, config, "test_operation")

        # All delays should be capped at max_delay
        assert len(call_times) == 4
        for i in range(1, len(call_times)):
            delay = call_times[i] - call_times[i - 1]
            # Should not exceed max_delay of 0.5s
            assert delay < 0.6

    @pytest.mark.asyncio
    async def test_jitter_adds_randomness(self):
        """Test that jitter adds randomness to delays."""
        delays = []

        for _ in range(5):
            call_times = []

            async def failing_operation():
                call_times.append(asyncio.get_event_loop().time())
                response = httpx.Response(
                    500, request=httpx.Request("GET", "http://test.com")
                )
                raise httpx.HTTPStatusError("", request=response.request, response=response)

            config = RetryConfig(
                max_attempts=2, initial_delay=0.1, backoff_factor=1.0, jitter=True
            )

            with pytest.raises(httpx.HTTPStatusError):
                await with_retry(failing_operation, config, "test_operation")

            if len(call_times) >= 2:
                delays.append(call_times[1] - call_times[0])

        # With jitter, delays should vary
        # They should all be in the range [0.05, 0.15] (50% to 150% of base delay)
        assert all(0.04 < d < 0.16 for d in delays)
        # Check that they're not all the same (probability of this is extremely low)
        assert len(set(delays)) > 1

    @pytest.mark.asyncio
    async def test_timeout_error_is_retried(self):
        """Test that timeout errors are retried."""
        call_count = 0

        async def timeout_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.TimeoutException("")
            return "success"

        config = RetryConfig(max_attempts=3, initial_delay=0.01)
        result = await with_retry(timeout_then_success, config, "test_operation")

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_network_error_is_retried(self):
        """Test that network errors are retried."""
        call_count = 0

        async def network_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.NetworkError("")
            return "success"

        config = RetryConfig(max_attempts=3, initial_delay=0.01)
        result = await with_retry(network_then_success, config, "test_operation")

        assert result == "success"
        assert call_count == 2
