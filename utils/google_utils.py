""" Description: This file contains the code to update a google sheet """
### IMPORTS ###
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_google_creds():
    """
    Function to get the google credentials
    """
    creds = None
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    token_path = "functions/token.json"
    credentials_path = "functions/credentials.json"
        # 
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds

def update_google_sheet(sheet_id, range_name, data):
    """
    Function to update a google sheet
    """
    creds = get_google_creds()

    print(" - - Google Sheets Update - - ")
    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .update(spreadsheetId=sheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=dict(
                    majorDimension='ROWS',  # The first dimension of the values array corresponds to rows
                    values=data  # The data to input
            ))
            .execute()
        )
        values = result.get("values",[])

        if not values:
            print(" - - Update Complete (No data returned)")
            return None

        print(" - - Update Compelte (returning data)")

        return values

    except HttpError as http_error:
        print(f"An http error occurred: {http_error}")
    
def clear_range(sheet_id, range_name):
    
    creds = get_google_creds()

    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    clear_body = {}
    sheet.values().clear(
        spreadsheetId=sheet_id,
        range=range_name,
        body=clear_body).execute()
    
    return None

def get_google_sheets_data(sheet_id, range_name):
    """
    Function to get Google Sheets data

    :param sheet_id: str: The sheet ID
    :param range_name: str: The range of the sheet

    :return: list: The data from the sheet
    """
    print(" - - Google Sheets Query")
    creds = get_google_creds()

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(
                spreadsheetId=sheet_id,
                range=range_name,
                dateTimeRenderOption="FORMATTED_STRING",
                majorDimension="ROWS",
                valueRenderOption="FORMATTED_VALUE"
            )
            .execute()
        )
        values = result.get("values", [])
        
        print(" - - Query Complete (returning data)")
        return values

    except HttpError as http_error:
        print(f"An http error occurred: {http_error}")
