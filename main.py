from lib.google_drive_api import list_accounts, get_credentials, get_service, select_account_by_number
from lib.project_manager import load_config, load_projects, save_projects, create_project, set_active_project
from lib.context_generator import generate_ai_context
from lib.project_files import list_project_files, search_and_add_files_to_project


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

