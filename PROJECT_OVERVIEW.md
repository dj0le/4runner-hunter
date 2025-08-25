# 📁 Project Structure

```
4runner-hunter/
├── 🚀 start-here/              # START HERE for setup
│   ├── README.md               # Welcome & next steps
│   └── SETUP_GUIDE.md          # Complete setup instructions
│
├── 💻 src/                     # All Python source code
│   ├── web_app.py              # Main Flask web application
│   ├── main.py                 # Command-line interface
│   ├── api_client.py           # Auto.dev API integration
│   ├── database.py             # SQLite database operations
│   ├── vin_analyzer.py         # VIN pattern analysis
│   ├── config.py               # Configuration management
│   │
│   ├── 🤖 Virtual Mechanic AI System
│   ├── virtual_mechanic.py     # AI diagnostic assistant
│   ├── manual_indexer.py       # PDF manual indexing
│   ├── mechanic_report_generator.py  # Report generation
│   ├── print_report.py         # Formatted report printing
│   ├── pdf_page_extractor.py   # Manual page extraction
│   │
│   ├── templates/              # HTML templates for web app
│   ├── tests/                  # Test suite
│   └── utils/                  # Database utilities
│
├── 📚 docs/                    # Documentation
│   ├── LEARNING_GUIDE.md       # Learning exercises & tutorials
│   ├── CONTRIBUTING.md         # Contribution guidelines
│   └── CLAUDE.md               # AI assistant instructions
│
├── 📂 Data Directories (created when needed)
├── manuals/                    # PDF service manuals (add your own)
├── reports/                    # Generated diagnostic reports
├── extracted_pages/            # Extracted manual pages
├── manual_summaries/           # Manual analysis summaries
├── chroma/                     # Vector database files
├── 4runner_mechanic_db/        # Vector database files
│
├── ⚙️ Configuration
├── .env.example               # Configuration template
├── .env                       # Your actual configuration (gitignored)
├── requirements.txt           # Python dependencies
├── .gitignore                 # Files to ignore in git
│
└── 📖 Documentation
    ├── README.md              # Project overview & learning objectives
    ├── LICENSE                # MIT License
    └── PROJECT_OVERVIEW.md    # This file
```

## 🎯 Getting Started

1. **New to this project?** → Go to `start-here/` directory
2. **Want to learn?** → Read `docs/LEARNING_GUIDE.md` after setup
3. **Want to contribute?** → See `docs/CONTRIBUTING.md`
4. **Ready to code?** → All Python files are in `src/`

## 🏃‍♂️ Quick Commands

```bash
# Setup (first time)
cp .env.example .env  # then edit with your API key

# Run the web app
cd src && python web_app.py

# Run tests
cd src && python tests/test_api.py
```

## 🎓 Learning Path

1. **Start Here** → `start-here/SETUP_GUIDE.md`
2. **Explore Code** → `src/` directory
3. **Learn More** → `docs/LEARNING_GUIDE.md`
4. **Contribute** → `docs/CONTRIBUTING.md`