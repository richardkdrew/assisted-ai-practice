#!/usr/bin/env python
"""
End-to-end test script for retry logic using the API.

This script makes requests to the error test endpoints, extracts trace IDs
from the responses, and then tests our retry logic implementation.
"""

import requests
import logging
import time
import subprocess
import sys
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
API_BASE_URL = "http://localhost:8000"


def make_error_request(error_type):
    """
    Make a request to the error test endpoint.

    Args:
        error_type: The type of error to generate (validation, connection, etc.)

    Returns:
        Tuple of (response, trace_id) or (None, None) if the request failed
    """
    url = f"{API_BASE_URL}/error-test/{error_type}"
    logger.info(f"Making request to {url}")

    try:
        response = requests.get(url)
        # Extract trace ID from response headers
        trace_id = None
        if 'traceparent' in response.headers:
            # traceparent format: 00-trace_id-span_id-01
            traceparent = response.headers['traceparent']
            trace_id = traceparent.split('-')[1]

        return response, trace_id
    except Exception as e:
        logger.error(f"Error making request: {e}")
        return None, None


def test_should_retry(trace_id):
    """
    Test the should_retry function using Python subprocess.

    Since we can't import directly due to environment issues, we'll use a subprocess.

    Args:
        trace_id: The trace ID to test

    Returns:
        The decision from should_retry or None if an error occurred
    """
    logger.info(f"Testing should_retry with trace_id: {trace_id}")

    # Command to run Python and execute our should_retry function
    cmd = [
        "docker", "exec", "configservice-app",
        "python", "-c",
        f"from observability.trace_retry.retry_logic import should_retry; "
        f"import json; "
        f"result = should_retry('{trace_id}'); "
        f"print(json.dumps(result))"
    ]

    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse the output
        if result.stdout:
            decision = json.loads(result.stdout.strip())
            return decision
        else:
            logger.error(f"No output from should_retry: {result.stderr}")
            return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running should_retry: {e}")
        logger.error(f"stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        logger.error(f"Output: {result.stdout}")
        return None


def test_error_type(error_type, expected_decision):
    """
    Test a specific error type and verify the retry decision.

    Args:
        error_type: The type of error to test
        expected_decision: The expected retry decision

    Returns:
        True if the test passed, False otherwise
    """
    logger.info(f"\n===== Testing {error_type} error =====")

    # Make the error request
    response, trace_id = make_error_request(error_type)

    if not trace_id:
        logger.error(f"Failed to get trace ID for {error_type} error")
        return False

    # Wait a moment for the trace to be processed
    logger.info("Waiting for trace to be processed...")
    time.sleep(2)

    # Test the should_retry function
    result = test_should_retry(trace_id)

    if not result:
        logger.error(f"Failed to get result from should_retry for {error_type} error")
        return False

    # Verify the decision
    actual_decision = result.get("decision")
    logger.info(f"Expected decision: {expected_decision}, Actual decision: {actual_decision}")

    if actual_decision == expected_decision:
        logger.info(f"✅ Test PASSED: {error_type} error correctly resulted in {actual_decision} decision")
        return True
    else:
        logger.error(f"❌ Test FAILED: {error_type} error resulted in {actual_decision} decision, expected {expected_decision}")
        return False


def run_tests():
    """Run all test cases."""
    # Test ValidationError (should return ABORT)
    validation_passed = test_error_type("validation", "ABORT")

    # Test ConnectionError (should return RETRY)
    connection_passed = test_error_type("connection", "RETRY")

    # Test for an unknown error type (should return WAIT)
    # We can use 'custom' which isn't explicitly mapped
    unknown_passed = test_error_type("custom", "WAIT")

    # Print summary
    logger.info("\n===== Test Summary =====")
    logger.info(f"ValidationError test: {'PASSED' if validation_passed else 'FAILED'}")
    logger.info(f"ConnectionError test: {'PASSED' if connection_passed else 'FAILED'}")
    logger.info(f"Unknown error test: {'PASSED' if unknown_passed else 'FAILED'}")

    # Return overall result
    return all([validation_passed, connection_passed, unknown_passed])


if __name__ == "__main__":
    logger.info("Starting retry logic API tests")
    success = run_tests()
    sys.exit(0 if success else 1)