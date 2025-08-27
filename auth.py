from google.oauth2 import service_account
from googleapiclient.discovery import build
import config


def get_authenticated_services():
    """
    Authenticate with Google APIs and return Forms and Sheets service objects.

    Returns:
        tuple: (forms_service, sheets_service)
    """
    try:
        # Load credentials from service account file
        credentials = service_account.Credentials.from_service_account_file(
            config.SERVICE_ACCOUNT_FILE,
            scopes=config.SCOPES
        )

        # Build service objects
        forms_service = build('forms', 'v1', credentials=credentials)
        sheets_service = build('sheets', 'v4', credentials=credentials)

        return forms_service, sheets_service

    except FileNotFoundError:
        print(
            f"Error: Service account file not found at {config.SERVICE_ACCOUNT_FILE}")
        print("Please download your service account JSON file from Google Cloud Console")
        return None, None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None, None
