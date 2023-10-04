from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO
from .google_drive_api import get_credentials, get_service


# Generate a flat text file containing all files' data in the project
def generate_ai_context(config, project):
    flat_file_content = ""

    # Create an empty list to hold file metadata and content
    file_metadata_content_list = []

    for file_info in project['files']:
        file_id = file_info['id']
        mime_type = file_info['mimeType']
        account_name = file_info['account']
        
        credentials = get_credentials(account_name, config)
        service = get_service(credentials)

        # Fetch additional metadata (modifiedTime, owners, lastModifyingUser)
        additional_metadata = service.files().get(fileId=file_id, fields='modifiedTime,owners,lastModifyingUser').execute()

        content = ""
        if "google-apps.document" in mime_type:
            # Handle Google Docs
            content = service.files().export(fileId=file_id, mimeType='text/plain').execute()
            content = content.decode('utf-8')

        elif "google-apps.presentation" in mime_type:
            # Handle Google Slides (For simplicity, fetching only slide titles)
            presentation = service.presentations().get(presentationId=file_id).execute()
            slides = presentation.get('slides', [])
            slide_titles = [slide.get('slideProperties', {}).get('title', 'Untitled slide') for slide in slides]
            content = ' | '.join(slide_titles)

        # Store metadata and content in a dictionary, then add to list
        file_metadata_content_list.append({
            'metadata': additional_metadata,
            'content': content,
            'mime_type': mime_type,
            'file_id': file_id
        })

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
        flat_file_content += f"Author: {author}\nEditor: {editor}\nModified Time: {modified_time}\n"
        
        if "google-apps.document" in mime_type:
            flat_file_content += f"{content}\n---\n"
        elif "google-apps.presentation" in mime_type:
            flat_file_content += f"{content}\n---\n"

    print(flat_file_content)
    return flat_file_content
