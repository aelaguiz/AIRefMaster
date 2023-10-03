from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


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
