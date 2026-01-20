import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import config
from googleapiclient.errors import HttpError


def get_drive_service():
    """
    Authenticate and return a Google Drive service object.

    Returns:
        Google Drive service object
    """
    try:
        credentials = service_account.Credentials.from_service_account_file(
            config.SERVICE_ACCOUNT_FILE,
            scopes=config.SCOPES
        )
        drive_service = build('drive', 'v3', credentials=credentials)
        return drive_service
    except Exception as e:
        print(f"Error authenticating with Google Drive: {e}")
        return None


def find_existing_file(service, filename, parent_folder_id):
    """Find an existing file with the given name in the parent folder and return its ID."""
    query = f"name='{filename}' and '{parent_folder_id}' in parents and trashed=false"
    try:
        results = service.files().list(
            q=query,
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        items = results.get('files', [])

        if items:
            return items[0]['id']  # Return the first match
        return None
    except HttpError as error:
        print(
            f"Warning: Could not search for existing file '{filename}': {error}")
        return None


def upload_files_to_drive(folder_id=None, local_folder='output'):
    """
    Upload all files from the local folder to a Google Drive folder.

    Args:
        folder_id (str): Google Drive folder ID. If None, files are uploaded to root.
        local_folder (str): Local folder path to upload from. Defaults to 'output'.

    Returns:
        list: List of uploaded file names
    """
    drive_service = get_drive_service()
    if not drive_service:
        print("Failed to get Drive service. Upload aborted.")
        return []

    if not os.path.exists(local_folder):
        print(f"Error: Local folder '{local_folder}' does not exist.")
        return []

    uploaded_files = []

    # Get all files in the output folder
    files_to_upload = [f for f in os.listdir(local_folder)
                       if os.path.isfile(os.path.join(local_folder, f))
                       and not f.startswith('.')]

    if not files_to_upload:
        print(f"No files found in '{local_folder}' to upload.")
        return []

    print(f"\n📤 Uploading {len(files_to_upload)} file(s) to Google Drive...")

    for filename in files_to_upload:
        try:
            file_path = os.path.join(local_folder, filename)

            # File metadata
            file_metadata = {
                'name': filename
            }

            # Add parent folder if specified
            if folder_id:
                file_metadata['parents'] = [folder_id]

            # Determine MIME type based on file extension
            mime_type = 'text/csv' if filename.endswith(
                '.csv') else 'application/octet-stream'

            media = MediaFileUpload(
                file_path, mimetype=mime_type, resumable=True)

            # Check if file already exists in Drive
            existing_file_id = find_existing_file(
                drive_service, filename, folder_id)

            if existing_file_id:
                # Update existing file
                file = drive_service.files().update(
                    fileId=existing_file_id,
                    media_body=media,
                    fields='id, name, webViewLink',
                    supportsAllDrives=True
                ).execute()
                print(
                    f"   🔄 Updated: {filename} (ID: {file.get('id')})")
                uploaded_files.append(filename)
            else:
                # Upload new file
                file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, name, webViewLink',
                    supportsAllDrives=True  # THIS IS A KEY LINE
                ).execute()

                uploaded_files.append(filename)
                print(f"   ✅ Uploaded: {filename} (ID: {file.get('id')})")

        except Exception as e:
            print(f"   ❌ Failed to upload {filename}: {e}")

    print(f"\n✨ Successfully uploaded {len(uploaded_files)} file(s)")
    return uploaded_files


def create_drive_folder(folder_name, parent_folder_id=None):
    """
    Create a new folder in Google Drive.

    Args:
        folder_name (str): Name of the folder to create
        parent_folder_id (str): ID of parent folder. If None, creates in root.

    Returns:
        str: ID of the created folder, or None if failed
    """
    drive_service = get_drive_service()
    if not drive_service:
        return None

    try:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]

        folder = drive_service.files().create(
            body=file_metadata,
            fields='id, name',
            supportsAllDrives=True
        ).execute()

        print(
            f"📁 Created folder: {folder.get('name')} (ID: {folder.get('id')})")
        return folder.get('id')

    except Exception as e:
        print(f"Error creating folder: {e}")
        return None
