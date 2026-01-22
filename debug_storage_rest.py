
import requests
import json

# CONFIG from app_config.js
URL = "https://nbpxmramqufvxiikxbve.supabase.co"
KEY = "sb_publishable_peLRGV8YGA5djczYBgLnkQ_buXXBknN"
BUCKET_ID = "nota grn" # With space

def list_bucket_files():
    print(f"Listing bucket: '{BUCKET_ID}' via REST API...")
    
    # Endpoint: /storage/v1/object/list/{bucket}
    # Handling space in bucket name usually requires encoding, likely 'nota%20grn'
    # requests library handles params encoding usually, but for path variable we might need manual.
    
    # Try 1: Encoded Space
    api_url = f"{URL}/storage/v1/object/list/nota%20grn" 
    
    headers = {
        "apikey": KEY,
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json"
    }
    
    body = {
        "prefix": "",
        "limit": 100,
        "sortBy": {"column": "name", "order": "desc"}
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=body)
        
        if response.status_code == 200:
            files = response.json()
            print(f"Files found: {len(files)}")
            with open("debug_file_list.txt", "w") as f_out:
                for f in files:
                    f_out.write(f['name'] + "\n")
            print("File list saved to 'debug_file_list.txt'. Please read it.")
        else:
            print(f"Error ({response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    list_bucket_files()
