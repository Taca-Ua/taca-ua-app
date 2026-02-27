"""
Test script for snapshot endpoints.

This script tests all internal snapshot endpoints to verify they are
properly implemented and responding correctly.

Usage:
    python test_snapshot_endpoints.py

Requirements:
    - All microservices must be running
    - Services must be accessible (either locally or via Docker network)
"""

import json
from typing import Any, Dict

import requests


def test_snapshot_endpoint(service_name: str, url: str) -> Dict[str, Any]:
    """
    Test a snapshot endpoint and return the result.

    Args:
        service_name: Name of the service (for logging)
        url: Full URL to the snapshot endpoint

    Returns:
        Dictionary with test result
    """
    print(f"\n{'='*60}")
    print(f"Testing {service_name} snapshot endpoint")
    print(f"URL: {url}")
    print(f"{'='*60}")

    try:
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            data = response.json()

            # Count records
            total_records = sum(
                len(v) if isinstance(v, list) else 0 for v in data.values()
            )

            print(f"✅ SUCCESS - Status: {response.status_code}")
            print("📊 Response structure:")
            for key, value in data.items():
                if isinstance(value, list):
                    print(f"   - {key}: {len(value)} records")
                else:
                    print(f"   - {key}: {type(value).__name__}")

            print(f"📈 Total records: {total_records}")

            return {
                "service": service_name,
                "success": True,
                "status_code": response.status_code,
                "total_records": total_records,
                "data_keys": list(data.keys()),
            }
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"Response: {response.text}")
            return {
                "service": service_name,
                "success": False,
                "status_code": response.status_code,
                "error": response.text,
            }

    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR - Cannot connect to {url}")
        print(f"Error: {str(e)}")
        return {
            "service": service_name,
            "success": False,
            "error": "Connection error",
            "details": str(e),
        }

    except requests.exceptions.Timeout as e:
        print("❌ TIMEOUT - Request took longer than 30 seconds")
        print(f"Error: {str(e)}")
        return {
            "service": service_name,
            "success": False,
            "error": "Timeout",
            "details": str(e),
        }

    except Exception as e:
        print("❌ ERROR - Unexpected error occurred")
        print(f"Error: {str(e)}")
        return {
            "service": service_name,
            "success": False,
            "error": "Unexpected error",
            "details": str(e),
        }


def main():
    """Run tests for all snapshot endpoints."""
    print("\n" + "=" * 60)
    print("SNAPSHOT ENDPOINTS TEST SUITE")
    print("=" * 60)

    # Service URLs - adjust these based on your environment
    # For Docker network: use service names (e.g., http://matches-service:8000)
    # For local testing: use localhost (e.g., http://localhost:8001)

    services = {
        "Matches Service": "http://localhost:8001/internal/snapshot",
        "Modalities Service": "http://localhost:8002/internal/snapshot",
        "Ranking Service": "http://localhost:8003/internal/snapshot",
        "Tournaments Service": "http://localhost:8005/internal/snapshot",
    }

    # Alternatively, for Docker network testing:
    # services = {
    #     "Matches Service": "http://matches-service:8000/internal/snapshot",
    #     "Tournaments Service": "http://tournaments-service:8000/internal/snapshot",
    #     "Modalities Service": "http://modalities-service:8000/internal/snapshot",
    #     "Ranking Service": "http://ranking-service:8000/internal/snapshot",
    # }

    results = []

    for service_name, url in services.items():
        result = test_snapshot_endpoint(service_name, url)
        results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    print(f"\n✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")

    if successful == len(results):
        print("\n🎉 All snapshot endpoints are working correctly!")
    else:
        print("\n⚠️  Some snapshot endpoints failed. Check the details above.")

    # Detailed results
    print("\n" + "-" * 60)
    print("DETAILED RESULTS:")
    print("-" * 60)
    for result in results:
        status = "✅" if result["success"] else "❌"
        service = result["service"]
        if result["success"]:
            records = result.get("total_records", 0)
            print(f"{status} {service}: {records} records")
        else:
            error = result.get("error", "Unknown error")
            print(f"{status} {service}: {error}")

    return results


if __name__ == "__main__":
    results = main()

    # Optional: Save results to JSON file
    with open("snapshot_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n📄 Results saved to snapshot_test_results.json")
