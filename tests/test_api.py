#!/usr/bin/env python3
"""Test script to debug Auto.dev API responses"""
import json
import requests
import sys
sys.path.append('..')
from config import API_KEY, API_BASE_URL, TARGET_YEARS

def test_api_connection():
    """Test basic API connectivity and response"""
    print(f"Testing Auto.dev API...")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"API Key: {'*' * 10}{API_KEY[-4:] if len(API_KEY) > 4 else 'NOT SET'}")
    print(f"Target Years: {TARGET_YEARS['min']}-{TARGET_YEARS['max']}")
    print("-" * 60)
    
    # Test 1: Basic request without filters
    print("\nTest 1: Basic 4Runner search (no year filter)")
    url = f"{API_BASE_URL}/listings"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": "4Runner Manual Hunter/1.0"
    }
    params = {
        "make": "Toyota",
        "model": "4Runner",
        "page": 1,
        "per_page": 10
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse Keys: {list(data.keys())}")
            print(f"Total Results: {data.get('total', 'N/A')}")
            print(f"Total Pages: {data.get('total_pages', 'N/A')}")
            listings = data.get('listings', data.get('results', []))
            print(f"Listings in this page: {len(listings)}")
            
            if listings:
                print("\nFirst listing sample:")
                print(json.dumps(listings[0], indent=2))
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")
    
    # Test 2: With year filter
    print("\n" + "-" * 60)
    print(f"\nTest 2: 4Runner search WITH year filter ({TARGET_YEARS['min']}-{TARGET_YEARS['max']})")
    params.update({
        "year_min": TARGET_YEARS["min"],
        "year_max": TARGET_YEARS["max"]
    })
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total Results: {data.get('total', 'N/A')}")
            print(f"Total Pages: {data.get('total_pages', 'N/A')}")
            listings = data.get('listings', data.get('results', []))
            print(f"Listings in this page: {len(listings)}")
            
            # Show year distribution
            if listings:
                years = {}
                for listing in listings:
                    year = listing.get('year', 'Unknown')
                    years[year] = years.get(year, 0) + 1
                print(f"\nYear distribution in this page: {years}")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")
    
    # Test 3: Try different API endpoints
    print("\n" + "-" * 60)
    print("\nTest 3: Testing different possible API endpoints")
    
    test_endpoints = [
        "/listings",
        "/vehicles",
        "/inventory",
        "/search",
        "/v1/listings",
        "/v2/listings"
    ]
    
    for endpoint in test_endpoints:
        test_url = f"{API_BASE_URL.rstrip('/')}{endpoint}"
        print(f"\nTrying: {test_url}")
        try:
            response = requests.get(test_url, headers=headers, params={"make": "Toyota", "model": "4Runner"}, timeout=5)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Success! Response has keys: {list(data.keys())[:5]}...")
        except Exception as e:
            print(f"  Failed: {str(e)}")
    
    # Test 4: Check API documentation endpoint
    print("\n" + "-" * 60)
    print("\nTest 4: Looking for API documentation")
    doc_endpoints = ["/", "/docs", "/documentation", "/api-docs", "/swagger"]
    for endpoint in doc_endpoints:
        try:
            response = requests.get(f"{API_BASE_URL.rstrip('/')}{endpoint}", headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"Found documentation at: {endpoint}")
        except:
            pass

if __name__ == "__main__":
    test_api_connection()