from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from dotenv import load_dotenv
import json  # Import the json module

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

def main():
    # Upload a file to Google Drive
    file_name = 'sub_benefits_renamed111.csv'  # Specify your file name here
    file_id = upload_file(file_name, mimetype='text/csv')

    # Share the uploaded file with an email address
    email_address = 'daniel.vuksanovic@themiracle.io'  # Specify the email address to share with
    share_file(file_id, email_address, role='writer')  # 'writer' role allows editing; 'reader' for view only

if __name__ == "__main__":
    main()
