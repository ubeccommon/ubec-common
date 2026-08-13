#!/usr/bin/env python3
"""
UBEC Holonic API Diagnostic Tool
================================
Diagnoses issues with holonic scores showing as 0% in the dashboard.

This script:
1. Tests the backend API holonic endpoint directly
2. Inspects the response structure
3. Identifies field mapping issues between backend and frontend
4. Suggests fixes based on findings

Usage:
    python diagnose_holonic_api.py --backend-url https://api.ubec.network
    python diagnose_holonic_api.py --backend-url http://92.205.230.245:8000

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our
    decisions and recommendations. This project was made possible with the
    assistance of Claude and Anthropic PBC.
"""

import asyncio
import argparse
import json
import sys
from typing import Any, Dict, Optional

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_json(data: Any, indent: int = 2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent, default=str))


async def test_holonic_endpoint(base_url: str) -> Optional[Dict]:
    """
    Test the holonic scores endpoint directly.
    
    Args:
        base_url: Backend API base URL
        
    Returns:
        Response data or None if failed
    """
    # Try multiple possible endpoint paths
    endpoints_to_try = [
        "/api/holonic/scores",
        "/api/v1/holonic/scores",
        "/v1/holonic-scores",
        "/holonic/scores",
        "/api/holonic-scores",
    ]
    
    print_header("Testing Holonic API Endpoints")
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_try:
            url = f"{base_url.rstrip('/')}{endpoint}"
            print(f"\n🔍 Testing: {url}")
            
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ SUCCESS - Status: {response.status}")
                        return {"url": url, "endpoint": endpoint, "data": data}
                    else:
                        text = await response.text()
                        print(f"   ❌ Status: {response.status} - {text[:100]}")
            except aiohttp.ClientConnectorError as e:
                print(f"   ❌ Connection error: {e}")
            except asyncio.TimeoutError:
                print(f"   ❌ Timeout")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    return None


def analyze_response_structure(data: Dict) -> Dict[str, Any]:
    """
    Analyze the API response structure to identify field mappings.
    
    Args:
        data: API response data
        
    Returns:
        Analysis results
    """
    print_header("Response Structure Analysis")
    
    analysis = {
        "top_level_keys": list(data.keys()),
        "has_ubuntu_principles": "ubuntu_principles" in data,
        "has_account_count": "account_count" in data,
        "has_accounts": "accounts" in data,
        "has_summary": "summary" in data,
        "potential_issues": [],
        "suggested_fixes": []
    }
    
    print("\n📋 Top-level keys in response:")
    for key in data.keys():
        value = data[key]
        value_type = type(value).__name__
        if isinstance(value, dict):
            sub_keys = list(value.keys())[:5]
            print(f"   • {key} ({value_type}): {sub_keys}")
        elif isinstance(value, list):
            print(f"   • {key} ({value_type}): {len(value)} items")
        else:
            print(f"   • {key} ({value_type}): {str(value)[:50]}")
    
    # Check for ubuntu_principles structure
    if "ubuntu_principles" in data:
        principles = data["ubuntu_principles"]
        print("\n🌍 Ubuntu Principles structure:")
        for key, value in principles.items():
            print(f"   • {key}: {value}")
            if isinstance(value, dict):
                if "average" in value:
                    avg = value.get("average", 0)
                    if avg == 0:
                        analysis["potential_issues"].append(
                            f"ubuntu_principles.{key}.average is 0"
                        )
    else:
        analysis["potential_issues"].append(
            "No 'ubuntu_principles' key found at top level"
        )
        
        # Look for principles elsewhere
        if "summary" in data and isinstance(data["summary"], dict):
            summary = data["summary"]
            if "ubuntu_principles" in summary:
                analysis["suggested_fixes"].append(
                    "ubuntu_principles is nested under 'summary' - update frontend parsing"
                )
            if "score_statistics" in summary:
                print("\n📊 Score Statistics found in summary:")
                print_json(summary["score_statistics"])
    
    # Check account_count
    if "account_count" in data:
        count = data["account_count"]
        print(f"\n👥 Account count: {count}")
        if count > 0:
            print("   ✅ Accounts are being evaluated")
    elif "pagination" in data:
        pagination = data["pagination"]
        if "total" in pagination:
            print(f"\n👥 Total accounts (from pagination): {pagination['total']}")
    
    return analysis


def check_frontend_expectations():
    """
    Document what the frontend (main_web.py) expects.
    """
    print_header("Frontend Expectations (main_web.py)")
    
    print("""
The frontend expects this response structure:

{
    "ubuntu_principles": {
        "diversity": {"average": 0.45},
        "reciprocity": {"average": 0.52},
        "mutualism": {"average": 0.38},
        "regeneration": {"average": 0.41}
    },
    "account_count": 500
}

Parsing code in main_web.py:
─────────────────────────────────────────────────
principles = raw_holonic_response.get('ubuntu_principles', {})
diversity = principles.get('diversity', {}).get('average', 0) or 0
reciprocity = principles.get('reciprocity', {}).get('average', 0) or 0
mutualism = principles.get('mutualism', {}).get('average', 0) or 0
regeneration = principles.get('regeneration', {}).get('average', 0) or 0
─────────────────────────────────────────────────
""")


def suggest_fixes(analysis: Dict, actual_data: Dict):
    """
    Suggest fixes based on analysis.
    """
    print_header("Diagnosis & Recommended Fixes")
    
    if analysis["potential_issues"]:
        print("\n⚠️  Potential Issues:")
        for issue in analysis["potential_issues"]:
            print(f"   • {issue}")
    
    if analysis["suggested_fixes"]:
        print("\n🔧 Suggested Fixes:")
        for fix in analysis["suggested_fixes"]:
            print(f"   • {fix}")
    
    # Check if scores exist but are actually zero
    if "ubuntu_principles" in actual_data:
        principles = actual_data["ubuntu_principles"]
        all_zeros = True
        for key in ["diversity", "reciprocity", "mutualism", "regeneration"]:
            if key in principles:
                val = principles[key]
                if isinstance(val, dict):
                    avg = val.get("average", 0)
                else:
                    avg = val
                if avg > 0:
                    all_zeros = False
        
        if all_zeros:
            print("\n🔴 ROOT CAUSE: All Ubuntu principle averages are genuinely 0")
            print("""
   This could mean:
   1. The holonic calculation algorithm isn't populating scores
   2. The accounts haven't been evaluated yet (check for cron job)
   3. The scoring criteria aren't being met by any accounts
   
   Check backend:
   - Is the holonic evaluation service running?
   - Are there scheduled jobs to calculate scores?
   - Check the holonic_evaluations table in the database
""")
    
    # Check for nested structure issue
    if "summary" in actual_data:
        summary = actual_data["summary"]
        if "score_statistics" in summary or "ubuntu_principles" in summary:
            print("\n🔵 STRUCTURE MISMATCH DETECTED")
            print("""
   The backend is returning data nested under 'summary' but the frontend
   expects it at the top level.
   
   FIX OPTION 1 - Update frontend (main_web.py):
   ──────────────────────────────────────────────
   summary = raw_holonic_response.get('summary', {})
   principles = summary.get('ubuntu_principles', {})
   # ... rest of parsing
   
   FIX OPTION 2 - Update backend API to flatten response
""")


async def main():
    parser = argparse.ArgumentParser(description="Diagnose UBEC Holonic API issues")
    parser.add_argument(
        "--backend-url",
        default="https://api.ubec.network",
        help="Backend API base URL"
    )
    args = parser.parse_args()
    
    if not AIOHTTP_AVAILABLE:
        print("❌ aiohttp is required. Install with: pip install aiohttp")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("  UBEC Holonic API Diagnostic Tool")
    print("=" * 60)
    print(f"\nBackend URL: {args.backend_url}")
    
    # Test endpoints
    result = await test_holonic_endpoint(args.backend_url)
    
    if result:
        print(f"\n✅ Found working endpoint: {result['endpoint']}")
        
        # Show full response
        print_header("Full API Response")
        print_json(result["data"])
        
        # Analyze structure
        analysis = analyze_response_structure(result["data"])
        
        # Show frontend expectations
        check_frontend_expectations()
        
        # Suggest fixes
        suggest_fixes(analysis, result["data"])
    else:
        print("\n❌ Could not connect to any holonic endpoint")
        print("""
Troubleshooting steps:
1. Check if backend server is running
2. Verify the API URL is correct
3. Check firewall/network connectivity
4. Look at backend logs for errors
""")


if __name__ == "__main__":
    asyncio.run(main())
