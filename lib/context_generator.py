from concurrent.futures import ThreadPoolExecutor
from functools import partial
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO
from .google_drive_api import get_credentials, get_service, fetch_file_content_and_metadata

def generate_ai_context(config, project):
    flat_file_content = ""
    file_metadata_content_list = []
    
    def fetch_file(file_info):
        file_id = file_info['id']
        mime_type = file_info['mimeType']  # Using mimeType from project's file_info
        account_name = file_info['account']

        print(f"Fetching file {file_id} from {account_name}...")
        
        additional_metadata, content = fetch_file_content_and_metadata(file_id, account_name, config, mime_type)

        return {
            'metadata': additional_metadata,
            'content': content,
            'mime_type': mime_type,
            'file_id': file_id
        }
    
    # Create a thread pool and map fetch_file to each file_info
    with ThreadPoolExecutor() as executor:
        file_metadata_content_list = list(executor.map(fetch_file, project['files']))

    # Sort list by modifiedTime
    file_metadata_content_list.sort(key=lambda x: x['metadata'].get('modifiedTime', ''))

    # Compile sorted content into flat_file_content
    for item in file_metadata_content_list:
        file_id = item['file_id']
        mime_type = item['mime_type']
        content = item['content']

        author = item['metadata'].get('owners', [{}])[0].get('displayName', 'Unknown')
        editor = item['metadata'].get('lastModifyingUser', {}).get('displayName', 'Unknown')
        modified_time = item['metadata'].get('modifiedTime', 'Unknown').split("T")[0]  # Just the date

        flat_file_content += f"=== {file_id} ===\n"
        flat_file_content += f"Author: {author}\nEditor: {editor}\nModified Time: {modified_time}\nType: {mime_type}\n"
        
        if "google-apps.document" in mime_type:
            flat_file_content += f"{content}\n---\n"
        elif "google-apps.presentation" in mime_type:
            flat_file_content += f"{content}\n---\n"

    print(flat_file_content)
    return flat_file_content
