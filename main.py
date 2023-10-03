from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import json

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Load JSON configuration
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)
    
# Get the Google API credentials for a given account
def get_credentials(account_name, config):
    creds = None
    credentials_file = config[account_name]["credentials_file"]
    token_file = f"{account_name}_token.pickle"

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return creds

# Initialize Google API client
def get_service(credentials):
    return build('drive', 'v3', credentials=credentials)

# List all accounts and their authentication status
def list_accounts(config):
    for account in config.keys():
        token_file = f"{account}_token.pickle"
        status = "Authenticated" if os.path.exists(token_file) else "Not Authenticated"
        print(f"{account} - {status}")

# Load project configuration from JSON
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

# Save project configuration to JSON
def load_projects():
    if os.path.exists("projects.json"):
        with open("projects.json", "r") as f:
            return json.load(f)
    return {}

# Save project configuration to JSON
def save_projects(projects):
    with open("projects.json", "w") as f:
        json.dump(projects, f)

# Create a new project
def create_project(projects):
    name = input("Enter the name of the new project: ")
    projects[name] = {"active": False}
    save_projects(projects)
    print(f"Created project: {name}")

# Set the active project
def set_active_project(projects):
    if not projects:
        print("No projects available to set active.")
        return

    choices = list(projects.keys())
    for i, proj in enumerate(choices, 1):
        print(f"{i}. {proj}")
    selection = int(input("Enter the number of the project to set active: ")) - 1
    for project in projects:
        projects[project]["active"] = False
    projects[choices[selection]]["active"] = True
    save_projects(projects)

# List files in the project
def list_project_files(service, project):
    if not project['files']:
        print("No files added to the project.")
        return

    print("Files in the current project:")
    for file_id in project['files']:
        file_info = service.files().get(fileId=file_id).execute()
        print(f"{file_info['name']} ({file_info['id']})")


# Search for and add files to the project
def search_and_add_files_to_project(config, project, projects):
    account_name = select_account_by_number(config)

    credentials = get_credentials(account_name, config)
    service = get_service(credentials)

    query = input("Enter the search string: ")
    results = service.files().list(q=f"name contains '{query}'", fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])

    if not items:
        print("No files found.")
        return

    existing_file_ids = {file['id']: True for file in project.get('files', [])}

    print("Search results:")
    for i, item in enumerate(items, 1):
        already_added = " (Already in project)" if item['id'] in existing_file_ids else ""
        print(f"{i}. {item['name']} ({item['id']}){already_added}")

    if 'files' not in project:
        project['files'] = []

    selection = input("Enter the numbers of the files to add to the project, separated by commas: ").split(',')
    for s in selection:
        index = int(s.strip()) - 1
        file_info = {
            'id': items[index]['id'],
            'mimeType': items[index]['mimeType'],
            'account': account_name
        }
        project['files'].append(file_info)

    
    save_projects(projects)  # Save the updated project information

# List project files with additional information
def list_project_files(config, active_project):
    if not active_project.get('files'):
        print("No files added to the project.")
        return

    print("Files in the current project:")
    for file_entry in active_project['files']:
        account_name = file_entry['account']
        file_id = file_entry['id']
        credentials = get_credentials(account_name, config)
        if credentials.valid:
            service = get_service(credentials)
            try:
                file_info = service.files().get(fileId=file_id).execute()
                print(f"{file_info['name']} ({file_info['id']}) from account {account_name}")
            except Exception as e:
                print(f"Could not retrieve file {file_id} from account {account_name}: {e}")

# Choose account by number
def select_account_by_number(config):
    print("Available accounts:")
    account_names = list(config.keys())
    for i, account in enumerate(account_names, 1):
        print(f"{i}. {account}")
    selection = int(input("Enter the number of the account: ")) - 1
    if 0 <= selection < len(account_names):
        return account_names[selection]
    else:
        print("Invalid selection.")
        return None


from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO

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

# Main program loop
if __name__ == '__main__':
    config = load_config()
    projects = load_projects()
    active_project = [proj for proj, data in projects.items() if data.get("active")]

    while True:
        prompt = f"[ACTIVE PROJECT: {active_project[0] if active_project else 'None'}] > "
        
        print("\nOptions:")
        print("1 - List Google accounts and OAuth status")
        print("2 - Authenticate to a Google account")
        print("3 - Create a new project")
        print("4 - Set an active project")
        print("5 - List all files in the current project")
        print("6 - Search for files to add to the current project")
        print("7 - Generate AI context from current project")
        print("8 - Exit")

        
        choice = input(prompt)


        if choice == "1":
            list_accounts(config)
        elif choice == "2":
            account_name = select_account_by_number(config)
            if account_name:
                get_credentials(account_name, config)
                print(f"Authenticated to {account_name}")
        elif choice == "3":
            create_project(projects)
        elif choice == "4":
            set_active_project(projects)
            active_project = [proj for proj, data in projects.items() if data.get("active")]
        elif choice == "5":
            if not active_project:
                print("No active project. Set a project active first.")
            else:
                list_project_files(config, projects[active_project[0]])
        elif choice == "6":
            if not active_project:
                print("No active project. Set a project active first.")
            else:
                search_and_add_files_to_project(config, projects[active_project[0]], projects)
        elif choice == "7":
            if not active_project:
                print("No active project. Set a project active first.")
            else:
                generate_ai_context(config, projects[active_project[0]])
        elif choice == "8":
            break

