import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google API settings
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SCOPES = [
    'https://www.googleapis.com/auth/forms.body.readonly',
    'https://www.googleapis.com/auth/forms.responses.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

# Form settings (set in .env file)
FORM_ID = os.getenv('FORM_ID')
# Optional: if responses go to a sheet
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Output settings
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
