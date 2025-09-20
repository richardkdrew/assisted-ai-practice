#!/usr/bin/env python3
"""Simple test script using curl commands to test the API."""

import subprocess
import json
import time
import sys
from ulid import ULID

def run_curl(method, url, data=None, timeout=10):
    """Run a curl command and return the result."""
    cmd = ["curl", "-s", "-X", method, url]

    if data:
        cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(data)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response", "raw": result.stdout}
        else:
            return {"error": f"Curl failed with code {result.returncode}", "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "Request timed out"}
    except Exception as e:
        return {"error": f"Exception: {e}"}

def test_api():
    """Test the API using curl commands."""
    base_url = "http://localhost:8000"

    print("🔍 Testing Configuration Service API with curl")
    print("=" * 60)

    # Test health endpoint
    print("\n1. Testing health endpoint...")
    health = run_curl("GET", f"{base_url}/health")
    if "error" in health:
        print(f"❌ Health check failed: {health['error']}")
        print("💡 Make sure the server is running: python run_test_app.py")
        return False

    print(f"✅ Health check passed: {health.get('status', 'unknown')}")

    # Test application creation
    print("\n2. Testing application creation...")
    app_data = {
        "name": f"test-app-{ULID()}",
        "comments": "Test application created via curl"
    }

    created_app = run_curl("POST", f"{base_url}/api/v1/applications/", app_data)
    if "error" in created_app:
        print(f"❌ Application creation failed: {created_app['error']}")
        return False

    print(f"✅ Application created: {created_app.get('name', 'unknown')}")
    app_id = created_app.get('id')
    if not app_id:
        print("❌ No application ID returned")
        return False

    # Test application retrieval
    print("\n3. Testing application retrieval...")
    retrieved_app = run_curl("GET", f"{base_url}/api/v1/applications/{app_id}")
    if "error" in retrieved_app:
        print(f"❌ Application retrieval failed: {retrieved_app['error']}")
        return False

    print(f"✅ Application retrieved: {retrieved_app.get('name', 'unknown')}")
    print(f"   Configuration count: {len(retrieved_app.get('configuration_ids', []))}")

    # Test configuration creation
    print("\n4. Testing configuration creation...")
    config_data = {
        "application_id": app_id,
        "name": f"test-config-{ULID()}",
        "comments": "Test configuration created via curl",
        "config": {
            "database": {"host": "localhost", "port": 5432},
            "features": ["feature1", "feature2"],
            "timeout": 30.5
        }
    }

    created_config = run_curl("POST", f"{base_url}/api/v1/configurations/", config_data)
    if "error" in created_config:
        print(f"❌ Configuration creation failed: {created_config['error']}")
        return False

    print(f"✅ Configuration created: {created_config.get('name', 'unknown')}")
    config_id = created_config.get('id')

    # Test configuration retrieval
    print("\n5. Testing configuration retrieval...")
    retrieved_config = run_curl("GET", f"{base_url}/api/v1/configurations/{config_id}")
    if "error" in retrieved_config:
        print(f"❌ Configuration retrieval failed: {retrieved_config['error']}")
        return False

    print(f"✅ Configuration retrieved: {retrieved_config.get('name', 'unknown')}")
    config_obj = retrieved_config.get('config', {})
    print(f"   Database host: {config_obj.get('database', {}).get('host', 'unknown')}")

    # Test application list
    print("\n6. Testing application list...")
    app_list = run_curl("GET", f"{base_url}/api/v1/applications/")
    if "error" in app_list:
        print(f"❌ Application list failed: {app_list['error']}")
        return False

    total = app_list.get('total', 0)
    print(f"✅ Application list retrieved: {total} total applications")

    # Test documentation
    print("\n7. Testing API documentation...")
    docs_response = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{base_url}/docs"],
        capture_output=True, text=True
    )

    if docs_response.stdout == "200":
        print("✅ API documentation accessible at http://localhost:8000/docs")
    else:
        print(f"❌ Documentation not accessible (HTTP {docs_response.stdout})")

    print("\n" + "=" * 60)
    print("🎉 All basic API tests completed successfully!")
    print("\n📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")

    return True

def main():
    """Run the simple curl-based test."""
    try:
        success = test_api()
        if success:
            print("\n✅ Simple API test completed successfully")
            sys.exit(0)
        else:
            print("\n❌ Simple API test failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()