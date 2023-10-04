import json
import os

# Load JSON configuration
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
    for project in projects:
        projects[project]["active"] = False
    projects[name] = {"active": True}
    
    print(f"Created project: {name} and set it as active.")
    save_projects(projects)

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
