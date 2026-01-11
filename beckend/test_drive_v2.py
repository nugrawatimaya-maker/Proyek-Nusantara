import json
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

print("Mulai Diagnosa...", flush=True)

CRED_FILE = "credentials.json"
# Hardcode folder ID dari yang user kasih tadi untuk testing
FOLDER_ID = "1r0GFdwfWBsYlPRhOSLPtOHn_LVLJzyaW" 

try:
    with open(CRED_FILE, 'r') as f:
        data = json.load(f)
        email = data.get('client_email')
        print(f"EMAIL BOT: {email}", flush=True)
except Exception as e:
    print(f"Gagal baca credentials: {e}", flush=True)
    exit(1)

try:
    print(f"Mengakses Folder: {FOLDER_ID}", flush=True)
    scopes = ['https://www.googleapis.com/auth/drive.file']
    creds = Credentials.from_service_account_file(CRED_FILE, scopes=scopes)
    service = build('drive', 'v3', credentials=creds)

    folder = service.files().get(fileId=FOLDER_ID, fields="id, name").execute()
    print(f"[SUCCESS] Folder ditemukan: {folder.get('name')}", flush=True)
    
except Exception as e:
    print(f"[GAGAL] Error: {e}", flush=True)
