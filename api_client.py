import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from config import (
    API_KEY, API_BASE_URL, API_RATE_LIMIT_REQUESTS,
    API_RATE_LIMIT_WINDOW_SECONDS, API_RETRY_MAX_ATTEMPTS,
    API_RETRY_DELAY_SECONDS
)

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter to respect API limits."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    def wait_if_needed(self):
        """Wait if we've hit the rate limit."""
        now = datetime.now()
        # Remove old requests outside the window
        self.requests = [
            req_time for req_time in self.requests 
            if (now - req_time).total_seconds() < self.window_seconds
        ]
        
        if len(self.requests) >= self.max_requests:
            # Calculate how long to wait
            oldest_request = min(self.requests)
            wait_time = self.window_seconds - (now - oldest_request).total_seconds()
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time + 0.1)  # Add small buffer
        
        self.requests.append(now)


class AutoDevAPI:
    """Client for Auto.dev API."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "4Runner Manual Hunter/1.0"
        })
        self.rate_limiter = RateLimiter(
            API_RATE_LIMIT_REQUESTS, 
            API_RATE_LIMIT_WINDOW_SECONDS
        )
        self.api_calls_count = 0
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Optional[Dict]:
        """Make an API request with rate limiting and retry logic."""
        url = f"{API_BASE_URL}{endpoint}"
        
        for attempt in range(API_RETRY_MAX_ATTEMPTS):
            try:
                # Rate limiting
                self.rate_limiter.wait_if_needed()
                
                # Make request
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=30
                )
                
                self.api_calls_count += 1
                
                # Handle different status codes
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"API rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                elif response.status_code == 401:
                    logger.error("Authentication failed. Check your API key.")
                    return None
                else:
                    logger.error(f"API request failed: {response.status_code} - {response.text}")
                    
                    if attempt < API_RETRY_MAX_ATTEMPTS - 1:
                        time.sleep(API_RETRY_DELAY_SECONDS)
                        continue
                    return None
                    
            except requests.RequestException as e:
                logger.error(f"Request error: {str(e)}")
                if attempt < API_RETRY_MAX_ATTEMPTS - 1:
                    time.sleep(API_RETRY_DELAY_SECONDS)
                    continue
                return None
        
        return None
    
    def get_4runner_listings(self, page: int = 1, per_page: int = 20) -> Optional[Dict]:
        """Get Toyota 4Runner listings from the API."""
        params = {
            "make": "Toyota",
            "model": "4Runner",
            "page": page,
            "per_page": per_page
        }
        
        # Add year filter if configured
        from config import TARGET_YEARS, SEARCH_ZIP_CODE, SEARCH_LATITUDE, SEARCH_LONGITUDE
        if TARGET_YEARS["min"]:
            params["year_min"] = TARGET_YEARS["min"]
        if TARGET_YEARS["max"]:
            params["year_max"] = TARGET_YEARS["max"]
            
        # Add location parameters for distance calculation
        if SEARCH_ZIP_CODE:
            params["zip"] = SEARCH_ZIP_CODE
        elif SEARCH_LATITUDE and SEARCH_LONGITUDE:
            params["lat"] = float(SEARCH_LATITUDE)
            params["lon"] = float(SEARCH_LONGITUDE)
        
        logger.info(f"Fetching 4Runner listings page {page}...")
        return self._make_request("GET", "/listings", params=params)
    
    def get_all_4runner_listings(self) -> List[Dict]:
        """Get all Toyota 4Runner listings, handling pagination."""
        all_listings = []
        page = 1
        
        while True:
            response = self.get_4runner_listings(page=page)
            
            if not response:
                logger.error(f"Failed to fetch page {page}")
                break
            
            # Auto.dev API uses 'records' instead of 'listings'
            listings = response.get("records", response.get("listings", []))
            if not listings:
                break
            
            all_listings.extend(listings)
            
            # Check if there are more pages based on total count
            total_count = response.get("totalCount", 0)
            per_page = 20  # We request 20 per page
            total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
            
            logger.info(f"Fetched page {page}/{total_pages} - {len(listings)} listings (Total: {total_count})")
            
            if page >= total_pages or len(listings) < per_page:
                break
            
            page += 1
            time.sleep(1)  # Be nice to the API
        
        logger.info(f"Total listings fetched: {len(all_listings)}")
        return all_listings
    
    def decode_vin(self, vin: str) -> Optional[Dict]:
        """Decode a VIN to get detailed vehicle information."""
        if not vin or len(vin) != 17:
            logger.warning(f"Invalid VIN: {vin}")
            return None
        
        logger.debug(f"Decoding VIN: {vin}")
        return self._make_request("GET", f"/vin/{vin}")
    
    def get_api_calls_count(self) -> int:
        """Get the total number of API calls made."""
        return self.api_calls_count
    
    def reset_api_calls_count(self):
        """Reset the API calls counter."""
        self.api_calls_count = 0