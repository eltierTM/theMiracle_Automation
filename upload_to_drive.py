from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from dotenv import load_dotenv
import json  # Import the json module
import glob

# Load environment variables
load_dotenv()

def build_drive_service():
    """Builds the Drive service using credentials from the .env file."""
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if creds_json:
        creds_dict = json.loads(creds_json)  # Parse the JSON string into a Python dictionary
        creds = service_account.Credentials.from_service_account_info(creds_dict)
    else:
        raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable is not set or empty.")
    return build('drive', 'v3', credentials=creds)

def upload_file(filename, mimetype='text/csv'):
    """Uploads a file to Google Drive and returns the file ID."""
    service = build_drive_service()
    
    file_metadata = {'name': filename}
    media = MediaFileUpload(filename, mimetype=mimetype)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    print('File ID:', file_id)
    return file_id

def share_file(file_id, email_address, role='reader'):
    """Shares a file with the given email address using the Drive API."""
    service = build_drive_service()
    file_permission = {
        'type': 'user',
        'role': role,
        'emailAddress': email_address
    }
    try:
        service.permissions().create(
            fileId=file_id,
            body=file_permission,
            fields='id'
        ).execute()
        print(f"File {file_id} shared with {email_address} as a {role}.")
    except Exception as e:
        print(f"Failed to share file: {e}")

def get_latest_csv_filename(prefix="sub_benefits"):
    """Get the latest CSV filename based on the numerical suffix."""
    existing_files = glob.glob(f"{prefix}_*.csv")
    latest_file = None
    max_id = 0
    for file in existing_files:
        parts = os.path.basename(file).split('_')
        if len(parts) > 1 and parts[1].split('.')[0].isdigit():
            file_id = int(parts[1].split('.')[0])
            if file_id > max_id:
                max_id = file_id
                latest_file = file
    if not latest_file:
        raise FileNotFoundError("No CSV file found.")
    return latest_file

def main():
    # Determine the latest file name to upload
    file_name = get_latest_csv_filename()
    file_id = upload_file(file_name, mimetype='text/csv')

    # Share the uploaded file with an email address
    email_address = 'daniel.vuksanovic@themiracle.io'  # Specify the email address to share with
    share_file(file_id, email_address, role='writer')  # 'writer' role allows editing; 'reader' for view only

    print(f"Uploaded and shared file {file_name} successfully.")

if __name__ == "__main__":
    main()
