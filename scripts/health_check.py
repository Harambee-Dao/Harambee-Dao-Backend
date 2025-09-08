#!/usr/bin/env python3
"""
Health check script for deployed Harambee DAO Backend
Usage: python scripts/health_check.py [URL]
"""

import sys
import requests
import json
from datetime import datetime

def check_endpoint(url: str, endpoint: str, expected_status: int = 200) -> dict:
    """Check a specific endpoint and return results."""
    full_url = f"{url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    try:
        response = requests.get(full_url, timeout=10)
        
        return {
            "endpoint": endpoint,
            "url": full_url,
            "status_code": response.status_code,
            "success": response.status_code == expected_status,
            "response_time": response.elapsed.total_seconds(),
            "content": response.text[:200] if response.text else None
        }
    except requests.exceptions.RequestException as e:
        return {
            "endpoint": endpoint,
            "url": full_url,
            "status_code": None,
            "success": False,
            "error": str(e),
            "response_time": None
        }

def main():
    """Main health check function."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "https://harambee-dao-backend.onrender.com"
    
    print(f"🏥 Health Check for Harambee DAO Backend")
    print(f"🌐 URL: {base_url}")
    print(f"⏰ Time: {datetime.now().isoformat()}")
    print("="*60)
    
    # Define endpoints to check
    endpoints = [
        ("health", "/health"),
        ("api_ping", "/api/ping"),
        ("api_testall", "/api/testall"),
        ("docs", "/docs"),
        ("openapi", "/openapi.json")
    ]
    
    results = []
    all_healthy = True
    
    for name, endpoint in endpoints:
        print(f"\n🔍 Checking {name}...")
        result = check_endpoint(base_url, endpoint)
        results.append(result)
        
        if result["success"]:
            print(f"  ✅ {result['status_code']} - {result['response_time']:.2f}s")
            if result.get("content"):
                try:
                    # Try to parse JSON response
                    json_content = json.loads(result["content"])
                    print(f"  📄 Response: {json.dumps(json_content, indent=2)[:100]}...")
                except:
                    print(f"  📄 Response: {result['content'][:100]}...")
        else:
            all_healthy = False
            if result.get("error"):
                print(f"  ❌ Error: {result['error']}")
            else:
                print(f"  ❌ {result['status_code']} - Unexpected status")
    
    # Summary
    print("\n" + "="*60)
    print("📊 HEALTH CHECK SUMMARY")
    print("="*60)
    
    healthy_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        endpoint = result["endpoint"]
        if result["success"]:
            print(f"  {status} {endpoint} - {result['response_time']:.2f}s")
        else:
            print(f"  {status} {endpoint} - FAILED")
    
    print(f"\n📈 Overall Status: {healthy_count}/{total_count} endpoints healthy")
    
    if all_healthy:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        return 0
    else:
        print("⚠️  SOME ISSUES DETECTED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
