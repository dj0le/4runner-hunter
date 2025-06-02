#!/usr/bin/env python3
"""Setup script for first-time users"""
import os
import sys
import shutil

def setup_project():
    """Help new users set up the project"""
    print("🚗 Toyota 4Runner Hunter Setup")
    print("=" * 50)
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("✅ Creating .env file from template...")
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("📝 Please edit .env with your Auto.dev API key and preferences")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    
    # Check for virtual environment
    if not os.path.exists('venv'):
        print("\n💡 Virtual environment not found. Creating one...")
        os.system(f"{sys.executable} -m venv venv")
        print("✅ Virtual environment created")
        print("📝 Please activate it with: source venv/bin/activate")
    else:
        print("✅ Virtual environment exists")
    
    # Check for requirements
    try:
        import flask, requests, sqlite3
        print("✅ Required packages appear to be installed")
    except ImportError:
        print("❌ Some required packages are missing")
        print("📝 Please run: pip install -r requirements.txt")
    
    print("\n🎯 Next Steps:")
    print("1. Get an API key from https://auto.dev")
    print("2. Edit .env and add your AUTO_DEV_API_KEY")
    print("3. Add your SEARCH_ZIP_CODE for distance calculations")
    print("4. Run: python main.py (for one-time search)")
    print("5. Run: python web_app.py (for web dashboard)")
    
    print("\n📚 Full documentation available in README.md")
    
    return True

if __name__ == "__main__":
    setup_project()