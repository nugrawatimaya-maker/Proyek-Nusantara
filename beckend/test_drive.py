
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load env
load_dotenv()

FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
CRED_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "credentials.json"

print("--- DIAGNOSA KONEKSI GOOGLE DRIVE ---")
print(f"1. Memeriksa File Credentials: {CRED_FILE}")

if not os.path.exists(CRED_FILE):
    print("[ERROR] File credentials.json TIDAK DITEMUKAN!")
    exit(1)

try:
    with open(CRED_FILE, 'r') as f:
        data = json.load(f)
        email = data.get('client_email')
        print(f"[OK] Credentials Valid. Email Service Account:")
        print(f"   EMAIL BOT: {email}")
        print(f"   (Pastikan email DI ATAS ini yang Anda tambahkan sebagai EDITOR di Folder Drive)")
except Exception as e:
    print(f"[ERROR] ERROR membaca credentials: {e}")
    exit(1)

print(f"\n2. Memeriksa Folder ID: {FOLDER_ID}")
if not FOLDER_ID:
    print("[ERROR] GOOGLE_DRIVE_FOLDER_ID belum diset di .env")
    exit(1)

print("3. Mencoba Menghubungi Google Drive...")
try:
    scopes = ['https://www.googleapis.com/auth/drive.file']
    creds = Credentials.from_service_account_file(CRED_FILE, scopes=scopes)
    service = build('drive', 'v3', credentials=creds)

    # Cek Metadata Folder
    folder = service.files().get(fileId=FOLDER_ID, fields="id, name, webViewLink, owners").execute()
    print(f"[OK] SUKSES! Bot bisa melihat folder ini.")
    print(f"   Nama Folder: {folder.get('name')}")
    print(f"   Link Folder: {folder.get('webViewLink')}")
    print(f"   Pemilik: {folder.get('owners')[0].get('displayName')}")
    
    print("\n4. Mencoba Upload Dummy File...")
    file_metadata = {
        'name': 'Tes_Koneksi_Bot.txt',
        'parents': [FOLDER_ID]
    }
    media = None 
    
    from googleapiclient.http import MediaIoBaseUpload
    import io
    
    file_content = b"Halo, ini tes dari bot Proyek Nusantara."
    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='text/plain')
    
    new_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"[OK] UPLOAD BERHASIL! File ID: {new_file.get('id')}")
    print("   Silakan cek folder Drive Anda, ada file 'Tes_Koneksi_Bot.txt'.")
    
    service.files().delete(fileId=new_file.get('id')).execute()
    print("   (File tes sudah dihapus kembali)")

except Exception as e:
    print(f"\n[GAGAL] GAGAL MENGAKSES DRIVE!")
    print(f"Pesan Error: {e}")
    print("\nSOLUSI:")
    print("1. Cek kembali Folder ID di .env apakah sudah benar.")
    print("2. PASTI email 'tangan-bot@...' sudah dijadikan EDITOR di folder tersebut.")
    print("3. Jika error 404, itu PASTI masalah sharing permission.")

print("\n--- DIAGNOSA SELESAI ---")

