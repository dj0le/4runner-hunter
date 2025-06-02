# Toyota 4Runner Manual Hunter

A streamlined Python application that tracks all Toyota 4Runners (1984-2002) from auto.dev API listings, with special focus on finding manual transmissions. It uses VIN pattern analysis to help identify mis-categorizations in the api.

![4Runner Hunter Dashboard](docs/screenshot.png)

## Features

- **Smart VIN Analysis**: Identifies manual transmissions from VIN patterns
- **Auto-Initialization**: Web dashboard automatically runs initial search on first launch
- **Web Dashboard**: Clean, responsive interface for browsing and filtering all 4Runners (1984-2002)
- **Photo Gallery**: Full-size lightbox view with keyboard navigation
- **Distance Calculation**: Calculates distances from your location
- **Engine Identification**: Automatically identifies 22R-E, 3RZ-FE, 3VZ-E, and 5VZ-FE engines
- **Advanced Filtering**: Filter by generation, transmission, engine, mileage, distance
- **Complete Tracking**: Stores all 4Runners (manual and automatic) for comprehensive market view

## Requirements

- Python 3.8+
- Auto.dev API key (required)
- Virtual environment (recommended)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dj0le/4runner-hunter.git
   cd 4runner-hunter
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings (see Configuration section)
   ```

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


## Usage

### Quick Start
```bash
# Start the web dashboard (auto-initializes on first run)
python web_app.py
```
Then open http://localhost:5000

The dashboard will automatically:
- Check if the database is empty
- Run an initial search if needed
- Display all 4Runners from 1984-2002

### Manual Command-Line Search (Optional)
```bash
python main.py
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

### Listings Table
- Vehicle data with VIN analysis results
- Transmission detection source and confidence
- Engine information and specifications
- Distance calculations and location data

### Search Runs Table
- Search history and statistics
- API usage tracking

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

- `main.py`: Core search logic
- `web_app.py`: Flask dashboard with auto-initialization
- `vin_analyzer.py`: VIN pattern analysis
- `api_client.py`: Auto.dev API wrapper
- `database.py`: SQLite database operations
- `config.py`: Configuration management
- `setup.py`: Package setup
- `utils/`: Essential utilities (3 files)
- `tests/`: Active test suite (3 files)
- `scripts/`: Security pre-commit hook

## Known Limitations

- **GM84R model code**: Mixed manual/automatic (requires photo verification)
- **VIN decode accuracy**: Some auto.dev VIN data may be incorrect
- **Year coverage**: Designed specifically for 1984-2002 4Runners
- **US market focus**: VIN patterns are for US market vehicles

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and personal use only. Please respect auto.dev's terms of service and rate limits. The authors are not responsible for any misuse of this software.

## Support

- 📖 Check the [documentation](docs/)
- 🐛 Report bugs via [GitHub Issues](https://github.com/yourusername/4runner-hunter/issues)
- 💬 Discussions welcome in [GitHub Discussions](https://github.com/yourusername/4runner-hunter/discussions)

---

Built with ❤️ for the Toyota 4Runner community
