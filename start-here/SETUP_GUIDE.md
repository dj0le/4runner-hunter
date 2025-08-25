# 🚀 Complete Setup Guide: From Zero to Running

**Starting from scratch? This guide will walk you through every step to get the 4Runner Hunter running on your development machine.**

## 📋 Prerequisites Check

Before we start, make sure you have:
- **Python 3.8 or higher** installed
- **Git** installed
- **A text editor** (VS Code, PyCharm, or any editor you prefer)
- **Internet connection** for API calls

### Check Your Python Version
```bash
python --version
# Should show Python 3.8.x or higher
# If it shows Python 2.x, try:
python3 --version
```

## 🔧 Step 1: Clone the Repository

```bash
# Navigate to where you want the project
cd ~/Documents  # or wherever you keep projects

# Clone the repository
git clone https://github.com/your-username/4runner-hunter.git
cd 4runner-hunter

# Verify you're in the right place
ls -la
# You should see files like: main.py, web_app.py, requirements.txt, etc.
```

## 🐍 Step 2: Set Up Python Virtual Environment

**Why virtual environments?** They keep your project dependencies isolated from other Python projects.

```bash
# Create virtual environment
python -m venv venv
# If python command doesn't work, try: python3 -m venv venv

# Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) at the start of your command prompt
```

## 📦 Step 3: Install Dependencies

```bash
# Make sure you're in the project directory and venv is activated
pip install -r requirements.txt

# This will install:
# - Flask (web framework)
# - requests (HTTP client)
# - chromadb (vector database)
# - PyPDF2 (PDF processing)
# - python-dotenv (environment variables)
# - And other dependencies
```

If you get permission errors, try:
```bash
pip install --user -r requirements.txt
```

## 🔑 Step 4: Get Your Auto.dev API Key

### 4.1 Sign Up for Auto.dev
1. Go to [https://auto.dev](https://auto.dev)
2. Click "Sign Up" or "Get API Key"
3. Create an account (it's free!)
4. Navigate to your dashboard/API section
5. Copy your API key (it looks like: `sk_live_abc123...`)

### 4.2 Configure Your Environment
```bash
# Copy the example environment file
cp .env.example .env

# Open .env in your text editor
# VS Code users:
code .env

# Nano users:
nano .env

# Or use any text editor you prefer
```

### 4.3 Edit Your .env File
Find this line:
```
AUTO_DEV_API_KEY=your_auto_dev_api_key_here
```

Replace `your_auto_dev_api_key_here` with your actual API key:
```
AUTO_DEV_API_KEY=sk_live_abc123your_actual_key_here
```

**Optional configurations:**
```bash
# Add your zip code for distance calculations (recommended)
SEARCH_ZIP_CODE=12345

# Configure for your specific 4Runner (helps with virtual mechanic)
VEHICLE_YEAR=1989
VEHICLE_ENGINE=3.0L 3VZ-E V6
VEHICLE_TRANSMISSION=5-speed manual
```

Save and close the file.

## 🧪 Step 5: Test Your Setup

### 5.1 Test API Connectivity
```bash
# Run the API test
python tests/test_api.py

# Expected output:
# Testing Auto.dev API connection...
# ✓ API connection successful
# ✓ Successfully fetched 4Runner listings
```

If you see errors:
- **401 Unauthorized**: Check your API key in `.env`
- **Connection errors**: Check your internet connection
- **Module not found**: Make sure your virtual environment is activated

### 5.2 Test VIN Analysis
```bash
python tests/test_vin_anal.py

# Expected output:
# Testing VIN analysis patterns...
# ✓ Manual transmission patterns working
# ✓ Automatic transmission patterns working
```

## 🚀 Step 6: Run the Application

### 6.1 Start the Web Dashboard
```bash
# Navigate to the src directory
cd src
python web_app.py

# Expected output:
# * Running on http://127.0.0.1:5000
# * Debug mode: off
```

### 6.2 Open in Browser
1. Open your web browser
2. Go to: `http://localhost:5000`
3. You should see the 4Runner Hunter dashboard

**First run behavior:**
- The app will automatically search for 4Runners on first load
- This may take 30-60 seconds
- You'll see a "Searching..." message
- Results will appear when the search completes

## 🔧 Step 7: Set Up Virtual Mechanic (Optional but Recommended)

The Virtual Mechanic needs PDF service manuals to work properly.

### 7.1 Get Toyota Service Manuals
You need Toyota 4Runner PDF service manuals. Sources:
- **Official**: Toyota TechDoc or dealer service documentation
- **Third-party**: Haynes manuals, Chilton manuals
- **Online**: Forums often share factory service manuals

**Recommended manuals:**
- Factory Service Manual for your year
- Engine Repair Manual (3VZ-E, 5VZ-FE, etc.)
- Electrical Wiring Diagrams

### 7.2 Add Manuals to Project
```bash
# Put your PDF files in the manuals directory
# Example file names:
# manuals/Factory Service Manual 1989 Toyota 4Runner.pdf
# manuals/Engine Repair Manual 3VZ-E.pdf
# manuals/Electrical Wiring Diagram 1995 Toyota 4Runner.pdf
```

### 7.3 Index Your Manuals
```bash
# This processes PDFs and creates a searchable database
cd src  # if not already there
python manual_indexer.py

# Expected output:
# Processing manuals...
# ✓ Indexed: Factory Service Manual 1989 Toyota 4Runner.pdf (245 sections)
# ✓ Indexed: Engine Repair Manual 3VZ-E.pdf (89 sections)
# ✓ Total: 334 sections indexed
```

### 7.4 Test Virtual Mechanic
```bash
# Generate a fluid specifications report
cd src  # if not already there
python mechanic_report_generator.py

# Expected output:
# ✓ Generated: reports/fluid_checklist_20231201_143022.html
# ✓ Generated: reports/fluid_checklist_20231201_143022.md
```

## ✅ Verification Checklist

Make sure everything works:

- [ ] Virtual environment activated (`(venv)` in command prompt)
- [ ] Dependencies installed (`pip list` shows flask, requests, etc.)
- [ ] API key configured (check `.env` file)
- [ ] API test passes (`python tests/test_api.py`)
- [ ] Web dashboard loads (`http://localhost:5000`)
- [ ] 4Runner listings appear in dashboard
- [ ] (Optional) Manuals indexed and virtual mechanic working

## 🚨 Troubleshooting Common Issues

### Python Version Issues
```bash
# If python command uses Python 2.x
python3 -m venv venv
python3 -m pip install -r requirements.txt
python3 web_app.py
```

### Permission Errors on Windows
```bash
# Run as administrator or use:
pip install --user -r requirements.txt
```

### Virtual Environment Not Activating
```bash
# On Windows, try:
venv\Scripts\activate.bat

# Or use PowerShell:
venv\Scripts\Activate.ps1
```

### API Key Issues
- Make sure there are no spaces around the `=` in `.env`
- Make sure you copied the entire key
- Check that `.env` is in the project root directory

### Port Already in Use
```bash
# If port 5000 is busy, specify a different port:
python web_app.py
# Then edit web_app.py and change the port at the bottom:
# app.run(debug=True, host='0.0.0.0', port=5001)
```

### No Results in Dashboard
- Check your API key is valid
- Try running `python main.py` to see detailed logs
- Check Auto.dev API status
- Verify you have internet connection

## 🎯 What's Next?

Now that you're set up:

1. **Explore the Dashboard**: Try the filters and sorting options
2. **Check the Learning Guide**: Open `LEARNING_GUIDE.md` for exercises
3. **Try the Virtual Mechanic**: Generate diagnostic reports
4. **Read the Code**: Start with `web_app.py` to understand the flow

## 💬 Getting Help

If you're stuck:
1. Check the error messages carefully
2. Look at the troubleshooting section above
3. Create an issue on GitHub with:
   - Your operating system
   - Python version
   - Error message (if any)
   - What you were trying to do

Happy learning! 🎉