import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_KEY = os.getenv("AUTO_DEV_API_KEY", "your_auto_dev_api_key")
API_BASE_URL = "https://auto.dev/api"

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "4runner_tracker.db")

# Search Configuration
SEARCH_INTERVAL_MINUTES = int(os.getenv("SEARCH_INTERVAL_MINUTES", "60"))
SEARCH_RADIUS_MILES = os.getenv("SEARCH_RADIUS_MILES", None)
TARGET_YEARS = {
    "min": int(os.getenv("TARGET_YEAR_MIN", "1984")),
    "max": int(os.getenv("TARGET_YEAR_MAX", "2002"))
}

# Location Configuration
SEARCH_ZIP_CODE = os.getenv("SEARCH_ZIP_CODE", None)
SEARCH_LATITUDE = os.getenv("SEARCH_LATITUDE", None)
SEARCH_LONGITUDE = os.getenv("SEARCH_LONGITUDE", None)

# Notification Configuration
NOTIFICATION_METHODS = os.getenv("NOTIFICATION_METHODS", "email,slack").split(",")
EMAIL_TO = os.getenv("EMAIL_TO", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# API Rate Limiting
API_RATE_LIMIT_REQUESTS = int(os.getenv("API_RATE_LIMIT_REQUESTS", "100"))
API_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("API_RATE_LIMIT_WINDOW_SECONDS", "60"))
API_RETRY_MAX_ATTEMPTS = int(os.getenv("API_RETRY_MAX_ATTEMPTS", "3"))
API_RETRY_DELAY_SECONDS = int(os.getenv("API_RETRY_DELAY_SECONDS", "5"))