import os
import json
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

CRED_FILE = "credentials.json"
ENV_FILE = ".env"

def main():
    print("\n=============================================")
    print("   SETTING FOLDER GOOGLE DRIVE (OTOMATIS)")
    print("=============================================\n")

    # 1. Cek Credentials
    if not os.path.exists(CRED_FILE):
        print("[ERROR] File credentials.json tidak ditemukan!")
        return

    try:
        with open(CRED_FILE, 'r') as f:
            data = json.load(f)
            email = data.get('client_email')
    except:
        print("[ERROR] Gagal membaca credentials.json")
        return

    print("LANGKAH 1: SHARE FOLDER")
    print("Silakan Buka Google Drive Anda, buat folder baru (misal: 'Nota Proyek').")
    print("Klik Kanan Folder -> Bagikan (Share) -> Tambahkan Email berikut sebagai EDITOR:\n")
    print(f"   {email}\n")
    
    print("---------------------------------------------")
    folder_input = input("LANGKAH 2: Masukkan Link Folder atau ID Folder disini:\n> ").strip()
    
    # Ekstrak ID dari Link
    folder_id = folder_input
    if "drive.google.com" in folder_input: # Jika input berupa link
        # Pattern: folders/1... atau id=1...
        match = re.search(r'folders/([a-zA-Z0-9_-]+)', folder_input)
        if match:
            folder_id = match.group(1)
        else:
            match_id = re.search(r'id=([a-zA-Z0-9_-]+)', folder_input)
            if match_id:
                folder_id = match_id.group(1)
    
    print(f"\nMemeriksa ID: {folder_id} ...")

    # 2. Verifikasi Akses
    try:
        scopes = ['https://www.googleapis.com/auth/drive.file']
        creds = Credentials.from_service_account_file(CRED_FILE, scopes=scopes)
        service = build('drive', 'v3', credentials=creds)

        # Coba akses folder
        folder = service.files().get(fileId=folder_id, fields="id, name").execute()
        print(f"\n[SUKSES] Terhubung ke folder: {folder.get('name')}")
        
    except Exception as e:
        print(f"\n[GAGAL] Tidak bisa mengakses folder tersebut.")
        print(f"Penyebab: {e}")
        print("Pastikan email bot sudah dijadikan EDITOR di folder tersebut.")
        return

    # 3. Simpan ke .env
    print("\nLANGKAH 3: Menyimpan Konfigurasi...")
    
    # Baca .env lama
    env_content = ""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r') as f:
            env_content = f.read()
            
    # Update atau Tambah Variable
    new_line = f"GOOGLE_DRIVE_FOLDER_ID={folder_id}"
    
    if "GOOGLE_DRIVE_FOLDER_ID=" in env_content:
        # Replace existing line
        env_lines = env_content.splitlines()
        new_lines = []
        for line in env_lines:
            if line.startswith("GOOGLE_DRIVE_FOLDER_ID="):
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        env_content = "\n".join(new_lines)
    else:
        # Append new line
        env_content += f"\n{new_line}"
        
    with open(ENV_FILE, 'w') as f:
        f.write(env_content)
        
    print("[SELESAI] Konfigurasi berhasil disimpan!")
    print("Silakan RESTART server backend Anda sekarang.")

if __name__ == "__main__":
    main()
