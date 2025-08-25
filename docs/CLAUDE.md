# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Toyota 4Runner Manual Hunter with Virtual Mechanic - A specialized Python application that hunts for manual transmission Toyota 4Runners (1984-2002) by monitoring the Auto.dev API. It includes a comprehensive virtual mechanic system that indexes PDF service manuals and provides diagnostic assistance with printable reports and manual page extraction.

## Key Commands

### Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (includes ChromaDB, PyPDF2, grip for virtual mechanic)
pip install -r requirements.txt

# Set up configuration
cp .env.example .env
# Edit .env with AUTO_DEV_API_KEY (required)
# Add vehicle specifications for virtual mechanic
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

### Virtual Mechanic System
```bash
# Index PDF service manuals into ChromaDB
python manual_indexer.py

# Generate fluid specifications checklist
python mechanic_report_generator.py

# Print reports with formatting
python print_report.py <report_number>
python print_report.py <report_file>

# Print reports with manual page extraction
python print_report.py <report_number> --with-pages

# Extract manual pages only
python extract_manual_pages.py <report_file>

# Generate troubleshooting reports for symptoms
python -c "from mechanic_report_generator import MechanicReportGenerator; MechanicReportGenerator().generate_troubleshooting_report(['describe symptoms here'])"

# Analyze manual coverage
python manual_analyzer.py
```

### Database Management
```bash

# Reset database (WARNING: deletes all data)
python utils/reset_db.py

# View results from command line
python utils/view_results.py
```

## Architecture

### Core Components (20+ files total)

#### 4Runner Hunter Core
- **main.py**: Core search logic with VIN-focused strategy for 1984-2002 4Runners using Auto.dev API
- **web_app.py**: Flask dashboard with auto-initialization, filtering, sorting, and toast notifications for search feedback
- **vin_analyzer.py**: Pattern-based VIN analysis to identify transmissions without API calls
- **api_client.py**: Auto.dev API wrapper with rate limiting and exponential backoff
- **database.py**: SQLite storage with indexing for performance
- **config.py**: Central configuration management with vehicle specifications

#### Virtual Mechanic System
- **manual_indexer.py**: ChromaDB-powered PDF manual indexing with text extraction and semantic search
- **virtual_mechanic.py**: AI-powered diagnostic assistant with vehicle-specific filtering
- **mechanic_report_generator.py**: Automated report generation for fluids, maintenance, and troubleshooting
- **print_report.py**: Advanced HTML/PDF printing with formatting and manual page integration
- **pdf_page_extractor.py**: Smart extraction of referenced manual pages from PDFs
- **extract_manual_pages.py**: Command-line interface for manual page extraction
- **quick_diagnosis.py**: Rapid diagnostic report generation from symptoms
- **manual_analyzer.py**: Manual coverage analysis and summary generation

### Key Design Decisions

#### 4Runner Hunter
1. Web app auto-initializes with first search if database is empty
2. VIN pattern analysis to identify mis-categorizations in the Auto.dev API
3. All 1st generation 4Runners (1984-1989) are collected regardless of transmission
4. Collects ALL 4Runners from 1984-2002 (manual and automatic) for complete tracking
5. Toast notifications provide user-friendly feedback instead of popup alerts
6. Clean, streamlined codebase focused on Auto.dev API reliability

#### Virtual Mechanic
7. ChromaDB semantic search for intelligent manual content retrieval
8. Vehicle-specific filtering based on year, engine, and transmission
9. Automatic manual reference extraction for PDF page retrieval
10. Checklist-based reports for practical garage use
11. Integrated PDF page extraction preserves diagrams and tables
12. Print-optimized formatting removes GitHub styling and borders

### Database Schema
- **4runner_tracker.db**: SQLite database for vehicle listings and search runs
- **ChromaDB collection**: Indexed Toyota 4Runner service manual content (1013+ sections)
- **manual_summaries/**: Individual manual analysis and coverage reports
- **reports/**: Generated diagnostic and maintenance reports
- **extracted_pages/**: PDF manual pages extracted for specific diagnostics

## Development Tips

### Adding New VIN Patterns
Edit `vin_analyzer.py` and update the pattern dictionaries for the relevant model years. Test thoroughly with `tests/test_vin_anal.py`.

### Modifying Search Logic
The search flow: 
1. Auto.dev API: API search → Year filter (1984-2002) → VIN analysis → Store ALL results
2. Results displayed in dashboard with filtering and sorting options

### Virtual Mechanic Development
- **Adding new manuals**: Place PDFs in `manuals/` directory and run `python manual_indexer.py`
- **Custom reports**: Extend `MechanicReportGenerator` class with new report types
- **Manual references**: All reports automatically extract page references for PDF extraction
- **Print formatting**: CSS in `print_report.py` handles US Letter paper with clean formatting
- **Vehicle configuration**: Update `.env` file with vehicle specifications for targeted results

### Web Dashboard
- Auto-runs initial search if database is empty
- Refresh button runs Auto.dev searches with toast notifications for feedback
- Filters: Manual, 1st Gen, Auto, Generations, Mileage, Distance
- Sorts: Price, Year, Mileage, Days on Market, Distance
- Clean listing cards with Auto.dev links and dealer information
- Toast notifications provide smooth user feedback instead of popup alerts

### Virtual Mechanic Workflow
1. **Initial Setup**: Index PDF manuals with `manual_indexer.py`
2. **Generate Reports**: Use `mechanic_report_generator.py` for comprehensive diagnostics
3. **Print & Extract**: Use `print_report.py --with-pages` for complete documentation packages
4. **Quick Diagnosis**: Use `quick_diagnosis.py` for rapid symptom-based troubleshooting
