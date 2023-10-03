from .google_drive_api import list_accounts, get_credentials, get_service, select_account_by_number
from .project_manager import save_projects

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
