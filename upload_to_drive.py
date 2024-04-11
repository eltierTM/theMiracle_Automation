from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from dotenv import load_dotenv
import json
import glob

# Load environment variables
load_dotenv()

def build_drive_service():
    """Builds the Drive and Sheets service using credentials from the .env file."""
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if creds_json:
        creds_dict = json.loads(creds_json)
        scopes = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)
    else:
        raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable is not set or empty.")
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    return drive_service, sheets_service

def upload_csv_as_sheet(drive_service, filename, folder_id='1vYJFJYMQuvxa4ktF5n_AEsIT7xjh8DM-', mimetype='text/csv'):
    """Uploads a CSV file to Google Drive and converts it to a Google Sheets format."""
    file_metadata = {
        'name': os.path.basename(filename),
        'parents': [folder_id],
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    media = MediaFileUpload(filename, mimetype=mimetype, resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    print('Google Sheet ID:', file_id)
    return file_id

def add_sheets_to_spreadsheet(sheets_service, spreadsheet_id, sheet_titles):
    """Adds new sheets to an existing spreadsheet."""
    batch_update_spreadsheet_request_body = {
        'requests': [
            {'addSheet': {'properties': {'title': title}}} for title in sheet_titles
        ]
    }

    response = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=batch_update_spreadsheet_request_body
    ).execute()
    print(f"Added sheets: {sheet_titles}")

def get_latest_csv_filename(prefix="sub_benefits"):
    """Find the latest CSV file with a specified prefix."""
    existing_files = glob.glob(f"{prefix}_*.csv")
    latest_file = max(existing_files, key=os.path.getctime) if existing_files else None
    if not latest_file:
        raise FileNotFoundError("No CSV file found.")
    return latest_file

def main():
    folder_id = '1vYJFJYMQuvxa4ktF5n_AEsIT7xjh8DM-'
    drive_service, sheets_service = build_drive_service()
    file_name = get_latest_csv_filename()
    
    # Convert the CSV file to a Google Sheet and upload
    sheet_id = upload_csv_as_sheet(drive_service, file_name, folder_id)
    
    # Add additional sheets
    add_sheets_to_spreadsheet(sheets_service, sheet_id, ['Data_Coops_changed', 'Data_Coops_new'])

    print(f"Uploaded {file_name} as a Google Sheet and added additional sheets successfully.")

if __name__ == "__main__":
    main()
