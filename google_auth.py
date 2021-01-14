import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_google():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'google-credentials.json', scope)  # Your json file here
    gc = gspread.authorize(credentials)
    return(gc)