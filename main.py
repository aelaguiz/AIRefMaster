from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import json

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

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

def list_accounts(config):
    for account in config.keys():
        token_file = f"{account}_token.pickle"
        status = "Authenticated" if os.path.exists(token_file) else "Not Authenticated"
        print(f"{account} - {status}")

if __name__ == '__main__':
    config = load_config()

    while True:
        print("\nOptions:")
        print("1 - List Google accounts and OAuth status")
        print("2 - Authenticate to a Google account")
        print("3 - Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            list_accounts(config)
        elif choice == "2":
            print("Available accounts:")
            for account in config.keys():
                print(account)
            account_name = input("Enter the name of the account to authenticate: ")
            if account_name in config:
                get_credentials(account_name, config)
                print(f"Authenticated to {account_name}")
            else:
                print("Invalid account name")
        elif choice == "3":
            break
