#!/usr/bin/env python3
"""Manual test script to verify basic API functionality."""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add svc to path
sys.path.insert(0, str(Path(__file__).parent / "svc"))

import httpx
from ulid import ULID


async def test_api():
    """Test basic API functionality."""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        print("🔍 Testing Configuration Service API")
        print("=" * 50)

        # Test health endpoint
        print("\n1. Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed:", response.json())
            else:
                print("❌ Health check failed:", response.status_code)
                return False
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            print("💡 Make sure to start the API with: make run")
            return False

        # Test application creation
        print("\n2. Testing application creation...")
        app_data = {
            "name": f"test-app-{ULID()}",
            "comments": "Test application for manual verification"
        }

        response = await client.post(f"{base_url}/api/v1/applications/", json=app_data)
        if response.status_code == 201:
            created_app = response.json()
            print("✅ Application created successfully:")
            print(f"   ID: {created_app['id']}")
            print(f"   Name: {created_app['name']}")
            print(f"   Comments: {created_app['comments']}")
            app_id = created_app['id']
        else:
            print(f"❌ Application creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        # Test application retrieval
        print("\n3. Testing application retrieval...")
        response = await client.get(f"{base_url}/api/v1/applications/{app_id}")
        if response.status_code == 200:
            retrieved_app = response.json()
            print("✅ Application retrieved successfully:")
            print(f"   ID: {retrieved_app['id']}")
            print(f"   Configuration IDs: {retrieved_app['configuration_ids']}")
        else:
            print(f"❌ Application retrieval failed: {response.status_code}")
            return False

        # Test configuration creation
        print("\n4. Testing configuration creation...")
        config_data = {
            "application_id": app_id,
            "name": f"test-config-{ULID()}",
            "comments": "Test configuration",
            "config": {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "ssl": True
                },
                "features": ["feature1", "feature2"],
                "timeout": 30.5
            }
        }

        response = await client.post(f"{base_url}/api/v1/configurations/", json=config_data)
        if response.status_code == 201:
            created_config = response.json()
            print("✅ Configuration created successfully:")
            print(f"   ID: {created_config['id']}")
            print(f"   Name: {created_config['name']}")
            print(f"   Application ID: {created_config['application_id']}")
            config_id = created_config['id']
        else:
            print(f"❌ Configuration creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        # Test configuration retrieval
        print("\n5. Testing configuration retrieval...")
        response = await client.get(f"{base_url}/api/v1/configurations/{config_id}")
        if response.status_code == 200:
            retrieved_config = response.json()
            print("✅ Configuration retrieved successfully:")
            print(f"   ID: {retrieved_config['id']}")
            print(f"   Config keys: {list(retrieved_config['config'].keys())}")
            print(f"   Database host: {retrieved_config['config']['database']['host']}")
        else:
            print(f"❌ Configuration retrieval failed: {response.status_code}")
            return False

        # Test application list with configuration
        print("\n6. Testing application with linked configuration...")
        response = await client.get(f"{base_url}/api/v1/applications/{app_id}")
        if response.status_code == 200:
            app_with_config = response.json()
            if config_id in app_with_config['configuration_ids']:
                print("✅ Application correctly shows linked configuration")
            else:
                print("❌ Application does not show linked configuration")
                return False
        else:
            print(f"❌ Application retrieval failed: {response.status_code}")
            return False

        # Test application list
        print("\n7. Testing application list...")
        response = await client.get(f"{base_url}/api/v1/applications/")
        if response.status_code == 200:
            app_list = response.json()
            print(f"✅ Application list retrieved: {app_list['total']} total applications")
            print(f"   Has more: {app_list['has_more']}")
        else:
            print(f"❌ Application list failed: {response.status_code}")
            return False

        print("\n" + "=" * 50)
        print("🎉 All API tests passed successfully!")
        print("\n📚 API Documentation available at: http://localhost:8000/docs")
        return True


def main():
    """Run the manual test."""
    try:
        success = asyncio.run(test_api())
        if success:
            print("\n✅ Manual API test completed successfully")
            sys.exit(0)
        else:
            print("\n❌ Manual API test failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()