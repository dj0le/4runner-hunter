# Toyota 4Runner Manual Transmission Hunter - Project Plan

## Project Overview
Build an automated system to continuously monitor all Toyota 4Runner listings across the US and alert when manual transmission vehicles are found. Uses Auto.dev API for comprehensive coverage.

## Architecture

### Core Components
1. **Listing Fetcher** - Gets all 4Runner listings from Auto.dev
2. **VIN Decoder** - Checks each VIN for transmission type
3. **Database** - Stores listings and tracks processed vehicles
4. **Alert System** - Notifications for new manual finds
5. **Scheduler** - Runs searches automatically
6. **Web Dashboard** - View current findings (optional)

### Data Flow
```
Auto.dev Listings API → Filter 4Runners → VIN Decode → Check Manual → Store/Alert
```

## Technical Specifications

### API Integration
- **Base URL**: `https://auto.dev/api/`
- **Authentication**: Bearer token or query parameter
- **Key Endpoints**:
  - `GET /listings?make=Toyota&model=4Runner` - Get all 4Runner listings
  - `GET /vin/{VIN}` - Decode specific VIN for transmission data
- **Rate Limits**: TBD (monitor in testing)

### Database Schema
```sql
-- Listings table
CREATE TABLE listings (
    id INTEGER PRIMARY KEY,
    vin TEXT UNIQUE,
    year INTEGER,
    price INTEGER,
    mileage INTEGER,
    city TEXT,
    state TEXT,
    dealer_name TEXT,
    transmission_type TEXT,
    transmission_speeds INTEGER,
    engine_info TEXT,
    drivetrain TEXT,
    trim TEXT,
    first_seen DATETIME,
    last_seen DATETIME,
    is_manual BOOLEAN,
    notified BOOLEAN DEFAULT FALSE,
    raw_listing_data TEXT,
    raw_vin_data TEXT
);

-- Search history table
CREATE TABLE search_runs (
    id INTEGER PRIMARY KEY,
    run_timestamp DATETIME,
    total_listings_found INTEGER,
    new_listings INTEGER,
    manual_listings_found INTEGER,
    api_calls_made INTEGER,
    errors TEXT
);
```

### Configuration
```python
# config.py
API_KEY = "your_auto_dev_api_key"
DATABASE_PATH = "4runner_tracker.db"
SEARCH_INTERVAL_MINUTES = 60  # How often to run
NOTIFICATION_METHODS = ["email", "slack"]  # Alert channels
SEARCH_RADIUS_MILES = None  # None = nationwide
TARGET_YEARS = {
    "min": 1984,  # First year with manual option
    "max": 1995   # Last year with manual option
}
```

## Implementation Plan

### Phase 1: Core Functionality
1. **Setup project structure**
   ```
   4runner_hunter/
   ├── main.py              # Entry point
   ├── config.py            # Configuration
   ├── database.py          # Database operations
   ├── api_client.py        # Auto.dev API wrapper
   ├── vin_decoder.py       # VIN processing logic
   ├── notifications.py     # Alert system
   ├── scheduler.py         # Automated runs
   └── requirements.txt     # Dependencies
   ```

2. **Database setup**
   - Create SQLite database
   - Initialize tables
   - Add indexes for performance

3. **API client**
   - Wrapper for Auto.dev API calls
   - Rate limiting
   - Error handling and retries
   - Response validation

4. **Core search logic**
   - Fetch all 4Runner listings
   - Process VINs in batches
   - Identify manual transmissions
   - Store results

### Phase 2: Automation & Alerts
1. **Scheduling system**
   - Configurable search intervals
   - Logging and monitoring
   - Graceful error handling

2. **Notification system**
   - Email alerts for new finds
   - Slack/Discord webhooks
   - Alert templates with rich data

3. **Duplicate detection**
   - Track seen VINs
   - Handle price/location changes
   - Avoid spam notifications

### Phase 3: Enhancement
1. **Web dashboard** (optional)
   - Current inventory view
   - Search history
   - Manual configuration

2. **Advanced filtering**
   - Price ranges
   - Mileage limits
   - Geographic filtering
   - Specific trims/options

3. **Data enrichment**
   - Market value tracking
   - Price drop alerts
   - Historical trend analysis

## Key Functions

### Main Search Function
```python
def search_4runners():
    """Main search function"""
    # 1. Get all 4Runner listings
    # 2. Filter new/updated VINs
    # 3. Decode VINs for transmission data
    # 4. Store results
    # 5. Send notifications for manual finds
    # 6. Log search statistics
```

### VIN Processing
```python
def process_vin(vin):
    """Decode VIN and extract transmission data"""
    # 1. Call Auto.dev VIN API
    # 2. Extract transmission info
    # 3. Return structured data
```

### Alert System
```python
def send_manual_alert(listing_data):
    """Send notification for manual transmission find"""
    # 1. Format alert message
    # 2. Include key details (price, location, specs)
    # 3. Send via configured methods
```

## Expected Challenges & Solutions

### API Rate Limits
- **Challenge**: Auto.dev may have rate limits
- **Solution**: Implement exponential backoff, batch processing

### VIN Accuracy
- **Challenge**: Some listings may have incorrect/missing VINs  
- **Solution**: Validate VIN format, handle missing data gracefully

### Manual Transmission Detection
- **Challenge**: Ensuring accurate identification
- **Solution**: Check `transmissionType` field, validate against known manual configurations

### Data Volume
- **Challenge**: Processing thousands of listings efficiently
- **Solution**: Incremental updates, only decode new/changed VINs

## Success Metrics
- **Coverage**: Find all available manual 4Runners nationwide
- **Speed**: Complete search cycle in under 15 minutes
- **Accuracy**: 100% correct manual transmission identification
- **Reliability**: 99%+ uptime with error recovery
- **Alerting**: Notifications within 5 minutes of new listings

## Deployment Options
1. **Local Development**: Run on personal computer
2. **Cloud VPS**: DigitalOcean, Linode for 24/7 operation
3. **Serverless**: AWS Lambda with CloudWatch scheduling
4. **Raspberry Pi**: Low-cost always-on solution

## Timeline Estimate
- **Phase 1**: 2-3 days (core functionality)
- **Phase 2**: 1-2 days (automation & alerts)  
- **Phase 3**: 1-2 days (enhancements)
- **Total**: 4-7 days for complete system

## Next Steps
1. Set up development environment
2. Test API endpoints and understand response structure
3. Build and test core search functionality
4. Implement database storage
5. Add notification system
6. Deploy and monitor

## Manual 4Runner Context
**Years to Target**: 1984-2000 (manual transmission available)
**Transmission Types to Flag**:
- `transmissionType: "MANUAL"`
- Typically 4-speed or 5-speed
- May be labeled as "4M", "5M", "4-Speed Manual", "5-Speed Manual", "M/T", "STD"

**Why This Matters**: Manual transmission 4Runners are extremely rare and highly sought after by enthusiasts. Most were automatics, making manual examples valuable collector vehicles. Note: Manual transmissions became increasingly rare in the late 1990s models.
