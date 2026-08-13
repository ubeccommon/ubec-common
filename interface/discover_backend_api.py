#!/usr/bin/env python3
"""
Backend API Endpoint Discovery Tool
====================================

Discovers the actual API endpoints and structure of your backend.

Usage:
    python3 discover_backend_api.py
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional


async def discover_api(base_url: str = "http://92.205.230.245:8000"):
    """Discover backend API structure"""
    
    print("UBEC Backend API Discovery Tool")
    print("=" * 80)
    print(f"Backend URL: {base_url}\n")
    
    async with aiohttp.ClientSession() as session:
        
        # Try common API documentation endpoints
        print("🔍 Looking for API documentation...\n")
        
        doc_endpoints = [
            "/docs",
            "/api/docs",
            "/api/v1/docs",
            "/openapi.json",
            "/api/openapi.json",
            "/api/v1/openapi.json"
        ]
        
        for endpoint in doc_endpoints:
            url = f"{base_url}{endpoint}"
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        print(f"✅ Found: {url}")
                        print(f"   Status: {response.status}")
                        print(f"   Content-Type: {response.headers.get('content-type')}")
                        
                        if 'json' in response.headers.get('content-type', ''):
                            data = await response.json()
                            if 'paths' in data:
                                print(f"\n📋 Available endpoints:")
                                for path in sorted(data['paths'].keys()):
                                    methods = list(data['paths'][path].keys())
                                    print(f"   {path} [{', '.join(methods).upper()}]")
                                return data
            except:
                pass
        
        print("⚠️  No OpenAPI documentation found\n")
        
        # Try to discover endpoints manually
        print("🔍 Probing common endpoint patterns...\n")
        
        endpoints_to_try = [
            # Health checks
            ("/health", "Health Check"),
            ("/api/health", "Health Check (API)"),
            ("/api/v1/health", "Health Check (v1)"),
            ("/healthz", "Health Check (k8s style)"),
            
            # System/Status
            ("/status", "System Status"),
            ("/api/status", "System Status (API)"),
            ("/api/v1/status", "System Status (v1)"),
            ("/api/v1/system/status", "System Status (nested)"),
            
            # Network
            ("/network", "Network Info"),
            ("/api/network", "Network Info (API)"),
            ("/api/v1/network", "Network Info (v1)"),
            ("/api/v1/network/status", "Network Status"),
            ("/api/v1/network/stats", "Network Stats"),
            
            # Tokens
            ("/tokens", "Tokens"),
            ("/api/tokens", "Tokens (API)"),
            ("/api/v1/tokens", "Tokens (v1)"),
            
            # Transactions
            ("/transactions", "Transactions"),
            ("/api/transactions", "Transactions (API)"),
            ("/api/v1/transactions", "Transactions (v1)"),
            ("/api/v1/transactions/recent", "Recent Transactions"),
            
            # Bioregions
            ("/bioregions", "Bioregions"),
            ("/api/bioregions", "Bioregions (API)"),
            ("/api/v1/bioregions", "Bioregions (v1)"),
            
            # Holonic
            ("/holonic", "Holonic Scores"),
            ("/api/holonic", "Holonic Scores (API)"),
            ("/api/v1/holonic", "Holonic Scores (v1)"),
            ("/api/v1/holonic-scores", "Holonic Scores (hyphenated)"),
        ]
        
        working_endpoints = []
        
        for endpoint, name in endpoints_to_try:
            url = f"{base_url}{endpoint}"
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        print(f"✅ {endpoint:<35} -> {name}")
                        working_endpoints.append({
                            'endpoint': endpoint,
                            'name': name,
                            'status': response.status
                        })
                        
                        # Get sample response
                        try:
                            data = await response.json()
                            print(f"   Keys: {list(data.keys())[:5]}")  # First 5 keys
                        except:
                            pass
                    elif response.status == 404:
                        pass  # Silent - most will be 404
                    else:
                        print(f"⚠️  {endpoint:<35} -> Status: {response.status}")
            except Exception as e:
                pass  # Silent
        
        print(f"\n📊 Summary: Found {len(working_endpoints)} working endpoints")
        
        # Save results
        with open('/mnt/user-data/outputs/backend_endpoints.json', 'w') as f:
            json.dump(working_endpoints, f, indent=2)
        
        print(f"💾 Results saved to: backend_endpoints.json\n")
        
        # Now get detailed info from working endpoints
        if working_endpoints:
            print("=" * 80)
            print("DETAILED ENDPOINT ANALYSIS")
            print("=" * 80)
            
            for ep in working_endpoints:
                endpoint = ep['endpoint']
                url = f"{base_url}{endpoint}"
                
                print(f"\n📡 {endpoint}")
                print(f"   URL: {url}")
                
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Analyze structure
                            if isinstance(data, dict):
                                print(f"   Type: Dictionary")
                                print(f"   Keys: {list(data.keys())}")
                                
                                # Show sample values
                                for key, value in list(data.items())[:5]:
                                    if isinstance(value, (int, float, str, bool)):
                                        print(f"      - {key}: {type(value).__name__} = {value}")
                                    elif isinstance(value, list):
                                        print(f"      - {key}: list ({len(value)} items)")
                                    elif isinstance(value, dict):
                                        print(f"      - {key}: dict ({len(value)} keys)")
                            
                            elif isinstance(data, list):
                                print(f"   Type: List ({len(data)} items)")
                                if len(data) > 0 and isinstance(data[0], dict):
                                    print(f"   First item keys: {list(data[0].keys())}")
                except Exception as e:
                    print(f"   Error: {e}")
        
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print("\n1. Check if backend API has OpenAPI docs at:")
        print("   http://92.205.230.245:8000/docs")
        print("\n2. Update backend_client.py to use correct endpoint paths")
        print("\n3. If endpoints don't exist, backend API needs updating")


if __name__ == "__main__":
    asyncio.run(discover_api())
