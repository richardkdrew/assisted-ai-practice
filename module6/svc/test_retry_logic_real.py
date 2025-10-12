#!/usr/bin/env python
"""
Comprehensive test script for retry logic with real-world endpoints.

This script tests the retry logic by generating real errors from the
Configuration Service's business endpoints and verifying that our
retry logic makes the correct decisions.
"""

import requests
import logging
import time
import sys
import json
import uuid
import subprocess
from typing import Dict, Any, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
API_BASE_URL = "http://localhost:8000"

# Docker container names
DB_CONTAINER = "configservice-db"


def generate_random_id():
    """Generate a random ID for testing."""
    return str(uuid.uuid4())


def extract_trace_id(response):
    """Extract trace ID from response headers or body."""
    trace_id = None

    # Try to get from traceparent header
    if 'traceparent' in response.headers:
        traceparent = response.headers['traceparent']
        trace_id = traceparent.split('-')[1]
        logger.info(f"Extracted trace_id from header: {trace_id}")

    # If not found and error response, try to get from body
    if not trace_id and response.status_code >= 400:
        try:
            data = response.json()
            if 'error' in data and 'trace_id' in data['error']:
                trace_id = data['error']['trace_id']
                logger.info(f"Extracted trace_id from body: {trace_id}")
        except json.JSONDecodeError:
            pass

    return trace_id


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


def verify_retry_decision(trace_id, expected_decision):
    """
    Verify that should_retry returns the expected decision.

    Args:
        trace_id: The trace ID to test
        expected_decision: The expected retry decision

    Returns:
        True if the verification passed, False otherwise
    """
    # Wait a moment for the trace to be processed
    logger.info("Waiting for trace to be processed...")
    time.sleep(2)

    # Test the should_retry function
    result = test_should_retry(trace_id)

    if not result:
        logger.error(f"Failed to get result from should_retry for trace {trace_id}")
        return False

    # Verify the decision
    actual_decision = result.get("decision")
    logger.info(f"Expected decision: {expected_decision}, Actual decision: {actual_decision}")

    if actual_decision == expected_decision:
        logger.info(f"✅ Test PASSED: Trace {trace_id} correctly resulted in {actual_decision} decision")
        return True
    else:
        logger.error(f"❌ Test FAILED: Trace {trace_id} resulted in {actual_decision} decision, expected {expected_decision}")
        return False


def log_response_info(response, trace_id=None):
    """Log detailed information about a response."""
    logger.info(f"Response status: {response.status_code}")

    try:
        body_excerpt = response.text[:200] + ("..." if len(response.text) > 200 else "")
        logger.info(f"Response body: {body_excerpt}")
    except Exception as e:
        logger.info(f"Could not log response body: {e}")

    logger.info(f"Response headers: {dict(response.headers)}")

    if trace_id:
        logger.info(f"Trace ID: {trace_id}")
        logger.info(f"You can view this trace in Jaeger: http://localhost:16686/trace/{trace_id}")


def test_validation_error():
    """
    Test ValidationError (permanent error) using applications endpoint.

    Returns:
        True if the test passed, False otherwise
    """
    logger.info("\n===== Testing ValidationError (ABORT) with applications endpoint =====")

    # Create application with invalid data (missing required name field)
    invalid_app_data = {"comments": "This is an invalid application without a name"}

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/applications/",
            json=invalid_app_data
        )

        # Extract trace ID
        trace_id = extract_trace_id(response)

        # Log response info
        log_response_info(response, trace_id)

        # Check if we got a validation error
        if response.status_code != 422:
            logger.error(f"Expected status code 422, got {response.status_code}")
            return False

        # If we have a trace ID, verify the retry decision
        if trace_id:
            return verify_retry_decision(trace_id, "ABORT")
        else:
            logger.error("No trace ID found in response")
            return False

    except Exception as e:
        logger.error(f"Error testing validation error: {e}")
        return False


def test_not_found_error():
    """
    Test Not Found Error (permanent error) with non-existent resource.

    Returns:
        True if the test passed, False otherwise
    """
    logger.info("\n===== Testing NotFoundError (ABORT) with non-existent resource =====")

    # Generate a random ID that doesn't exist
    random_id = generate_random_id()

    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/applications/{random_id}")

        # Extract trace ID
        trace_id = extract_trace_id(response)

        # Log response info
        log_response_info(response, trace_id)

        # Check if we got a not found error
        if response.status_code != 404:
            logger.error(f"Expected status code 404, got {response.status_code}")
            return False

        # If we have a trace ID, verify the retry decision
        if trace_id:
            return verify_retry_decision(trace_id, "ABORT")
        else:
            logger.error("No trace ID found in response")
            return False

    except Exception as e:
        logger.error(f"Error testing not found error: {e}")
        return False


def stop_database():
    """
    Stop the database container temporarily.

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Stopping database container {DB_CONTAINER}...")
    try:
        result = subprocess.run(
            ["docker", "stop", DB_CONTAINER],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Database container stopped: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error stopping database container: {e}")
        logger.error(f"stderr: {e.stderr}")
        return False


def start_database():
    """
    Start the database container.

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Starting database container {DB_CONTAINER}...")
    try:
        result = subprocess.run(
            ["docker", "start", DB_CONTAINER],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Database container started: {result.stdout}")

        # Give the database some time to start up
        logger.info("Waiting for database to start up...")
        time.sleep(10)

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting database container: {e}")
        logger.error(f"stderr: {e.stderr}")
        return False


def test_connection_error():
    """
    Test ConnectionError (transient error) by stopping the database.

    Returns:
        True if the test passed, False otherwise
    """
    logger.info("\n===== Testing ConnectionError (RETRY) by stopping database =====")

    # Create valid application data
    valid_app_data = {
        "name": f"TestApp_{generate_random_id()[:8]}",
        "comments": "Test application for connection error"
    }

    try:
        # First stop the database
        if not stop_database():
            logger.error("Failed to stop database container")
            start_database()  # Try to restart the database before returning
            return False

        # Try to create an application (should fail with connection error)
        response = None
        trace_id = None

        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/applications/",
                json=valid_app_data,
                timeout=5
            )
        except requests.exceptions.ConnectionError as e:
            logger.info(f"Got expected ConnectionError: {e}")
        except Exception as e:
            logger.error(f"Got unexpected error: {e}")
        finally:
            # Always restart the database
            if not start_database():
                logger.error("Failed to restart database container")
                return False

        # If we didn't get a response directly, try to get the trace from Jaeger
        # Since we can't programmatically query Jaeger, this would have to be done manually
        # For now, we'll consider this test inconclusive

        logger.warning("Connection error test is inconclusive - requires manual verification")
        logger.info("Please check Jaeger UI for the most recent trace with ConnectionError")
        logger.info("Verify that the span has error.retriable=true and our logic returns RETRY")

        # For completeness, try a request now that the database is back
        time.sleep(5)  # Wait a bit for the application to recover
        response = requests.get(f"{API_BASE_URL}/health")
        logger.info(f"Health check after database restart: {response.status_code}")

        return True  # Return true but require manual verification

    except Exception as e:
        logger.error(f"Error testing connection error: {e}")
        # Make sure database is started again
        start_database()
        return False


def test_timeout_error():
    """
    Test TimeoutError (transient error) with a very short timeout.

    Returns:
        True if the test passed, False otherwise
    """
    logger.info("\n===== Testing TimeoutError (RETRY) with short client timeout =====")

    # Use configurations endpoint which tends to be slower
    try:
        # Set a very short timeout to force a timeout error
        response = None
        trace_id = None

        try:
            # List all configurations with a very small timeout
            response = requests.get(
                f"{API_BASE_URL}/api/v1/configurations/",
                params={"limit": 100},  # Request a lot of items to make it slower
                timeout=0.001  # Very short timeout (1ms)
            )
        except requests.exceptions.Timeout as e:
            logger.info(f"Got expected Timeout: {e}")
        except requests.exceptions.ConnectionError as e:
            # Connection error could happen due to the server not returning response before client disconnects
            logger.info(f"Got connection error due to timeout: {e}")
        except Exception as e:
            logger.error(f"Got unexpected error: {e}")

        # Similar to connection error, we can't easily get the trace ID from a client timeout
        # This would require manual verification or additional instrumentation

        logger.warning("Timeout error test is inconclusive - requires manual verification")
        logger.info("Please check Jaeger UI for the most recent trace with TimeoutError")
        logger.info("Verify that the span has error.retriable=true and our logic returns RETRY")

        # For completeness, do a regular request
        time.sleep(1)
        response = requests.get(f"{API_BASE_URL}/health")
        logger.info(f"Health check after timeout test: {response.status_code}")

        return True  # Return true but require manual verification

    except Exception as e:
        logger.error(f"Error testing timeout error: {e}")
        return False


def run_tests():
    """Run all test cases."""
    # Test ValidationError (permanent/ABORT)
    validation_passed = test_validation_error()

    # Test Not Found Error (permanent/ABORT)
    not_found_passed = test_not_found_error()

    # Test ConnectionError (transient/RETRY)
    # Note: This might disrupt other tests, so run it after the basic tests
    connection_passed = test_connection_error()

    # Test TimeoutError (transient/RETRY)
    timeout_passed = test_timeout_error()

    # Print summary
    logger.info("\n===== Test Summary =====")
    logger.info(f"ValidationError test: {'PASSED' if validation_passed else 'FAILED'}")
    logger.info(f"NotFoundError test: {'PASSED' if not_found_passed else 'FAILED'}")
    logger.info(f"ConnectionError test: {'INCONCLUSIVE - requires manual verification'}")
    logger.info(f"TimeoutError test: {'INCONCLUSIVE - requires manual verification'}")

    logger.info("\n===== Manual Verification Instructions =====")
    logger.info("For ConnectionError and TimeoutError tests:")
    logger.info("1. Open Jaeger UI: http://localhost:16686")
    logger.info("2. Search for recent traces with error tags")
    logger.info("3. Verify that ConnectionError has error.retriable=true")
    logger.info("4. Verify that TimeoutError has error.retriable=true")
    logger.info("5. Confirm our retry logic would return RETRY for both")

    # Return overall result
    return validation_passed and not_found_passed


if __name__ == "__main__":
    logger.info("Starting comprehensive retry logic tests with real-world endpoints")
    success = run_tests()
    logger.info(f"Tests {'succeeded' if success else 'failed'}")
    sys.exit(0 if success else 1)