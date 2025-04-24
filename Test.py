import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define scopes for Google Sheets + Drive access
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name(r"C:\Users\CraigVD\Downloads\eximreports-144806679823.json", scope)
client = gspread.authorize(creds)

sheet = client.open("UserFormMapping").sheet1

print("✅ Success! Spreadsheet title:", sheet.title)

import gspread
from oauth2client.service_account import ServiceAccountCredentials


