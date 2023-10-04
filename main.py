from lib.google_drive_api import list_accounts, get_credentials, get_service, select_account_by_number
from lib.project_manager import load_config, load_projects, save_projects, create_project, set_active_project
from lib.context_generator import generate_ai_context
from lib.project_files import list_project_files, search_and_add_files_to_project
from lib.pdf import text_to_pdf


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
                generated_content = generate_ai_context(config, projects[active_project[0]])

                while True:
                    print("\nWhat would you like to do with the generated content?")
                    print("1 - Save as txt")
                    print("2 - Save as pdf")
                    print("3 - Upload to s3 as txt")
                    print("4 - Upload to s3 as pdf")
                    print("5 - Exit this menu")
                    
                    sub_choice = input("> ")
                    if sub_choice == "1":
                        with open("output.txt", "w") as f:
                            f.write(generated_content)
                        print("Saved as output.txt.")
                    elif sub_choice == "2":
                        pdf_content = text_to_pdf(generated_content)
                        with open("output.pdf", "wb") as f:
                            f.write(pdf_content)
                        print("Saved as output.pdf.")
                    elif sub_choice == "3":
                        upload_to_s3(generated_content, 'txt', config)
                        print("Uploaded to S3 as txt.")
                    elif sub_choice == "4":
                        pdf_content = text_to_pdf(generated_content)
                        upload_to_s3(pdf_content, 'pdf', config)
                        print("Uploaded to S3 as pdf.")
                    elif sub_choice == "5":
                        break
                    else:
                        print("Invalid choice. Try again.")

        elif choice == "8":
            break

