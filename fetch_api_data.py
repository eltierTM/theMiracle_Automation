import requests
from dotenv import load_dotenv
import os
import csv
import glob

# Load environment variables from .env file
load_dotenv()

def authenticate():
    """Authenticate with the API to get a bearer token."""
    url = 'https://www.themiracle.io/api/auth'
    payload = {
        'email': os.getenv('THEMIRACLE_API_USERNAME'),
        'password': os.getenv('THEMIRACLE_API_PASSWORD')
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()['token']

def get_next_file_id(prefix="sub_benefits"):
    """Find the next available file ID based on existing files."""
    existing_files = glob.glob(f"{prefix}_*.csv")
    max_id = 0
    for file in existing_files:
        parts = os.path.basename(file).split('_')
        if len(parts) > 1 and parts[1].isdigit():
            max_id = max(max_id, int(parts[1]))
    return max_id + 1


def get_last_id(auth_token):
    """Get the last ID from the sub_benefits endpoint sorted by ID in descending order."""
    url = "https://www.themiracle.io/api/sub_benefits?order[id]=desc"
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    # Assuming the first item in the list is the one with the last ID
    if data and 'hydra:member' in data and data['hydra:member']:
        last_id = data['hydra:member'][0]['id']
        return last_id
    else:
        raise ValueError("Could not determine the last ID from the API response")

def fetch_sub_benefit(auth_token, id):
    """Fetch a sub-benefit by ID."""
    url = f"https://www.themiracle.io/api/sub_benefits/{id}"
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 404:  # Assuming 404 means not found
        return None
    response.raise_for_status()
    return response.json()

def write_to_csv(data):
    """Write the fetched data to a CSV file with a numerical suffix."""
    file_id = get_next_file_id()
    filename = f"sub_benefits_{file_id}.csv"
    # Include new keys for benefitSubcategoryNames and collectionName
    keys = ['id', 'shortTitle', 'longTitle', 'keywords', 'benefitSubcategoryNames', 'collectionName', 'shortDescription', 'longDescription', 'thumbnail', 'validFrom', 'validTo', 'status', 'url', 'tags', 'eventDate', 'location', 'actionDate', 'process', 'googleMapsUrl', 'URL of Source', 'changes made'] 
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        for item in data:
            if item:  # Ensure item is not None
                # Extract and format benefitSubcategoryNames
                subcategory_names = ', '.join([sub['name'] for sub in item.get('benefitSubcategories', [])])
                item['benefitSubcategoryNames'] = subcategory_names

                # Extract collectionName
                collection_name = item.get('collection', {}).get('name', '')
                item['collectionName'] = collection_name
                
                # Ensure every item has an empty "URL of Source" field
                item['URL of Source'] = item.get('URL of Source', '')
                writer.writerow({key: item.get(key, '') for key in keys})

                # Ensure every item has an empty "changes made" field
                item['changes made'] = item.get('changes made', '')
                writer.writerow({key: item.get(key, '') for key in keys})

    print(f"Data fetched and written to {filename} successfully.")


def main():
    token = authenticate()
    last_id = get_last_id(token)

    all_data = []
    for id in range(last_id + 1):  # Iterate from 0 to last ID
        item_details = fetch_sub_benefit(token, id)
        if item_details:  # Ensure item_details is not empty
            all_data.append(item_details)

    write_to_csv(all_data)
    print("Data fetched and written to CSV successfully.")

if __name__ == "__main__":
    main()
