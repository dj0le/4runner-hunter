# 🚙 Toyota 4Runner Manual Hunter

**A learning-focused Python application demonstrating AI-powered web scraping, data analysis, and diagnostic systems.**

Perfect for learning how to build real-world applications with modern Python tools and AI integration.

## 🎯 What This Project Teaches

### Core Development Skills
- **API Integration**: Auto.dev REST API with rate limiting and error handling
- **Web Scraping & Data Processing**: Smart VIN analysis and vehicle categorization
- **Database Design**: SQLite with proper indexing and relationships
- **Web Development**: Flask dashboard with real-time updates
- **AI Integration**: RAG (Retrieval-Augmented Generation) for intelligent document search

### Advanced Concepts
- **Vector Databases**: ChromaDB for semantic search of PDF manuals
- **PDF Processing**: Text extraction and intelligent content indexing
- **Rate Limiting**: Respectful API usage with exponential backoff
- **Data Visualization**: Clean web interfaces with filtering and sorting
- **Configuration Management**: Environment-based settings

## 🚀 Quick Start

**New to this project?** → See the **[📖 Complete Setup Guide](start-here/SETUP_GUIDE.md)** for step-by-step instructions.

### Already familiar with Python development?

```bash
# Clone and setup
git clone <this-repo>
cd 4runner-hunter
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Get API key from https://auto.dev/ then configure:
cp .env.example .env
# Edit .env: AUTO_DEV_API_KEY=your_key_here

# Run
cd src && python web_app.py
# Visit http://localhost:5000
```

### First time running?
The web dashboard will automatically:
1. Check if database is empty
2. Run initial Auto.dev search (may take 30-60 seconds)
3. Display all found 4Runners from 1984-2002

## 🏗️ Project Architecture

### 🔍 4Runner Hunter (Main Application)
Monitors the Auto.dev API for manual transmission Toyota 4Runners (1984-2002).

```
src/
├── web_app.py          # Flask dashboard with real-time search
├── api_client.py       # Auto.dev API client with rate limiting
├── database.py         # SQLite data layer
├── vin_analyzer.py     # Pattern-based VIN analysis
└── main.py             # Command-line search interface
```

**Key Learning Points:**
- How to build respectful API clients
- VIN decoding and pattern matching
- Real-time web dashboards with Flask
- Database design for time-series data

### 🔧 Virtual Mechanic (AI Diagnostic System)
AI-powered diagnostic assistant using RAG with Toyota service manuals.

```
src/
├── virtual_mechanic.py           # AI diagnostic interface
├── manual_indexer.py             # PDF indexing with ChromaDB
├── mechanic_report_generator.py  # Automated report generation
├── print_report.py               # Formatted report printing
└── pdf_page_extractor.py         # Smart manual page extraction
```

**Key Learning Points:**
- Vector databases and semantic search
- PDF text extraction and processing
- AI prompt engineering for diagnostics
- Document chunking strategies

## Configuration

### Required: Auto.dev API Key

1. Sign up at [auto.dev](https://auto.dev) for an API key
2. Free tier includes 10,000 API calls per month
3. Add your API key to `.env`:
   ```
   AUTO_DEV_API_KEY=your_api_key_here
   ```

### Optional: Location for Distance Calculation

Add your zip code for distance calculations:
```
SEARCH_ZIP_CODE=12345
```

Or use latitude/longitude:
```
SEARCH_LATITUDE=34.0522
SEARCH_LONGITUDE=-118.2437
```

### Optional: Vehicle Specifications for Virtual Mechanic

Configure your specific 4Runner for targeted diagnostic results:
```
VEHICLE_MAKE=Toyota
VEHICLE_MODEL=4Runner
VEHICLE_GENERATION=1st
VEHICLE_SERIES=N60
VEHICLE_YEAR=1989
VEHICLE_ENGINE=3.0L 3VZ-E V6
VEHICLE_TRANSMISSION=5-speed manual
VEHICLE_DRIVE_TYPE=4x4
```


## 🎯 Development Commands

### 4Runner Hunter (Web App)
```bash
# Navigate to source code
cd src

# Start web dashboard - automatically initializes database on first run
python web_app.py
# Then visit: http://localhost:5000

# Command-line search (optional)
python main.py

# View current results
python utils/view_results.py

# Reset database (WARNING: deletes all data)
python utils/reset_db.py
```

### Virtual Mechanic Setup (Optional)
```bash
# 1. Add Toyota PDF service manuals to manuals/ directory (project root)
# 2. Index the manuals for AI search
cd src
python manual_indexer.py

# 3. Generate diagnostic reports
python mechanic_report_generator.py

# 4. Print reports with clean formatting
python print_report.py <report_name>

# 5. Print with manual page extraction
python print_report.py <report_name> --with-pages
```

**Need manuals?** Look for Toyota Factory Service Manuals, Engine Repair guides, and Electrical Diagrams for your 4Runner year.

The dashboard will automatically:
- Check if the database is empty
- Run an initial Auto.dev search if needed
- Display all 4Runners from 1984-2002
- Provide toast notifications for search feedback

### Manual Command-Line Search (Optional)
```bash
python main.py
```

### Virtual Mechanic Usage
```bash
# Generate fluid specifications checklist
python mechanic_report_generator.py

# Generate troubleshooting report for symptoms
python -c "from mechanic_report_generator import MechanicReportGenerator; MechanicReportGenerator().generate_troubleshooting_report(['engine clicking noise wont start'])"

# Print reports with clean formatting
python print_report.py 1  # Print report #1
python print_report.py reports/fluid_checklist_final.md

# Print reports with manual page extraction
python print_report.py 1 --with-pages

# Extract only manual pages
python extract_manual_pages.py reports/starting_system_diagnosis.md

# Analyze manual coverage
python manual_analyzer.py
```

### Database Management
```bash
# View current results
python utils/view_results.py

# Reset database (WARNING: deletes all data)
python utils/reset_db.py

```

## How It Works

### VIN Pattern Analysis

The system uses Toyota VIN patterns to identify transmissions:

- **Positions 4-8** of the VIN contain model and transmission codes
- **Known manual patterns**: VN39W, RZN18, VZN18, etc.
- **Known automatic patterns**: HN87R, GN86R, GN87R, etc.
- **High accuracy**: 95%+ for known patterns

### Virtual Mechanic System

The AI-powered diagnostic system works through:

1. **PDF Indexing**: ChromaDB indexes Toyota service manual content with semantic search
2. **Vehicle-Specific Filtering**: Results tailored to your exact year/engine/transmission
3. **Report Generation**: Creates printable checklists with manual references
4. **Page Extraction**: Automatically extracts referenced PDF pages with diagrams
5. **Print Optimization**: Formats reports for clean US Letter printing

### Smart API Usage

- VIN patterns reduce API calls by ~70%
- Only uncertain vehicles require VIN decode API calls
- Rate limiting prevents API throttling
- Exponential backoff for error handling

### Engine Detection

Automatically identifies engines from VIN decode data:
- **22R-E**: 2.4L 4-cylinder
- **3RZ-FE**: 2.7L 4-cylinder
- **3VZ-E**: 3.0L V6
- **5VZ-FE**: 3.4L V6

## Database Schema

#### 4Runner Hunter Database
- **Listings Table**: Vehicle data with VIN analysis results, transmission detection, engine specs
- **Search Runs Table**: Search history and API usage tracking
- **File**: `4runner_tracker.db` (SQLite)

#### Virtual Mechanic Database
- **ChromaDB Collection**: 1000+ indexed manual sections with semantic search
- **Manual Summaries**: Individual manual analysis and topic coverage
- **Reports Directory**: Generated diagnostic and maintenance reports
- **Extracted Pages**: PDF manual pages with diagrams and tables

## API Usage

With the free tier (10,000 calls/month):
- **Initial search**: ~50-100 API calls
- **Daily monitoring**: ~10-20 API calls
- **VIN decode**: 1 call per unknown vehicle

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development

### Running Tests
```bash
# Test API connectivity
python tests/test_api.py

# Full system test
python tests/test_full_run.py

# VIN analysis tests
python tests/test_vin_anal.py
```

### Code Structure

#### Core 4Runner Hunter
- `main.py`: Core search logic
- `web_app.py`: Flask dashboard with auto-initialization
- `vin_analyzer.py`: VIN pattern analysis
- `api_client.py`: Auto.dev API wrapper
- `database.py`: SQLite database operations
- `config.py`: Configuration management with vehicle specs
- `utils/`: Essential utilities (2 files)
- `tests/`: Active test suite (3 files)

#### Virtual Mechanic System
- `manual_indexer.py`: PDF manual indexing with ChromaDB
- `virtual_mechanic.py`: AI diagnostic assistant
- `mechanic_report_generator.py`: Automated report generation
- `print_report.py`: Advanced printing with page extraction
- `pdf_page_extractor.py`: Manual page extraction engine
- `extract_manual_pages.py`: Command-line page extraction
- `manual_analyzer.py`: Manual coverage analysis
- `manuals/`: PDF service manual storage
- `reports/`: Generated diagnostic reports
- `extracted_pages/`: Extracted manual pages with diagrams

## Known Limitations

### 4Runner Hunter
- **GM84R model code**: Mixed manual/automatic (requires photo verification)
- **VIN decode accuracy**: Some auto.dev VIN data may be incorrect
- **Year coverage**: Designed specifically for 1984-2002 4Runners
- **US market focus**: VIN patterns are for US market vehicles

### Virtual Mechanic
- **Manual availability**: Requires Toyota PDF service manuals for full functionality
- **PDF text extraction**: Some scanned manuals may have poor text extraction
- **Manual compatibility**: Optimized for Toyota 4Runner service documentation
- **Print requirements**: Best results with US Letter paper and modern browsers

## 🎯 Final Project: AI Mechanic Web Integration

**Ready for the ultimate learning challenge?**

Transform the command-line Virtual Mechanic into a beautiful web interface! This capstone project brings together everything you've learned:

### What You'll Build
- 🔍 **Web-based AI diagnostics** - Ask questions through forms instead of terminal
- 📋 **One-click report generation** - Generate maintenance reports with buttons
- 📄 **In-browser viewing** - See professional reports in your web browser  
- 💾 **PDF downloads** - Get printable reports for garage use
- ✨ **Professional interface** - Modern, responsive design

### Learning Value
- **Full-stack development** (frontend + backend + AI)
- **AJAX and dynamic interfaces** 
- **File handling and downloads**
- **AI/ML web integration**
- **User experience design**

📖 **[Complete Final Project Guide →](docs/FINAL_PROJECT.md)**

*Transform terminal commands into a beautiful, professional web application!*

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and personal use only. Please respect Auto.dev's terms of service and rate limits. The authors are not responsible for any misuse of this software.

## Support

- 📖 Check the [documentation](docs/)
- 🐛 Report bugs via [GitHub Issues](https://github.com/yourusername/4runner-hunter/issues)
- 💬 Discussions welcome in [GitHub Discussions](https://github.com/yourusername/4runner-hunter/discussions)

---

Built with ❤️ for the Toyota 4Runner community
