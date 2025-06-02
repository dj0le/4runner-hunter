# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Toyota 4Runner Manual Hunter - A specialized Python application that hunts for manual transmission Toyota 4Runners (1984-2002) by monitoring auto.dev API listings. It uses VIN pattern analysis to identify transmissions.

## Key Commands

### Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp .env.example .env
# Edit .env with AUTO_DEV_API_KEY (required)
```

### Running the Application
```bash
# Web dashboard with auto-initialization (http://localhost:5000)
python web_app.py

# Manual command-line search (optional)
python main.py
```

### Testing
```bash
# Test API connectivity
python tests/test_api.py

# Full system test
python tests/test_full_run.py

# Test VIN analysis patterns
python tests/test_vin_anal.py
```

### Database Management
```bash

# Reset database (WARNING: deletes all data)
python utils/reset_db.py

# View results from command line
python utils/view_results.py
```

## Architecture

### Core Components (14 files total)
- **main.py**: Core search logic with VIN-focused strategy for 1984-2002 4Runners
- **web_app.py**: Flask dashboard with auto-initialization, filtering, sorting, and search refresh
- **vin_analyzer.py**: Pattern-based VIN analysis to identify transmissions without API calls
- **api_client.py**: Auto.dev API wrapper with rate limiting and exponential backoff
- **database.py**: SQLite storage with indexing for performance
- **config.py**: Central configuration management

### Key Design Decisions
1. Web app auto-initializes with first search if database is empty
2. VIN pattern analysis to identify mis-categorizations in the api
3. All 1st generation 4Runners (1984-1989) are collected regardless of transmission
4. Collects ALL 4Runners from 1984-2002 (manual and automatic) for complete tracking

### Database Schema
- **listings**: Stores all vehicle data (manual and automatic) with VIN analysis results
- **search_runs**: Tracks search history and statistics
- Single database file: `4runner_tracker.db`

## Development Tips

### Adding New VIN Patterns
Edit `vin_analyzer.py` and update the pattern dictionaries for the relevant model years. Test thoroughly with `tests/test_vin_anal.py`.

### Modifying Search Logic
The search flow: API search → Year filter (1984-2002) → VIN analysis → Store ALL results → Display in dashboard

### Web Dashboard
- Auto-runs initial search if database is empty
- Refresh button runs new searches
- Filters: Manual, 1st Gen, Auto, Generations, Mileage, Distance
- Sorts: Price, Year, Mileage, Days on Market, Distance
