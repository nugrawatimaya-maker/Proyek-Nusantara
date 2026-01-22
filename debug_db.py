
import os
from supabase import create_client, Client

# Credentials from app_config.js (PROD)
url: str = "https://nbpxmramqufvxiikxbve.supabase.co"
key: str = "sb_publishable_peLRGV8YGA5djczYBgLnkQ_buXXBknN"

supabase: Client = create_client(url, key)

target_po = "PO/NLD/2026/01/9727"

print(f"--- DEBUGGING PO: {target_po} ---")

# LIST FILES IN BUCKET
try:
    print("--- START STORAGE DEBUG ---")
    
    # Try 1: 'nota grn'
    print("\nAttempting to list bucket: 'nota grn'")
    try:
        res = supabase.storage.from_("nota grn").list() 
        print(f"Result type: {type(res)}")
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error listing 'nota grn': {e}")

    # Try 2: 'nota-grn'
    print("\nAttempting to list bucket: 'nota-grn'")
    try:
        res = supabase.storage.from_("nota-grn").list() 
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error listing 'nota-grn': {e}")

    # Try 3: 'nota_grn'
    print("\nAttempting to list bucket: 'nota_grn'")
    try:
        res = supabase.storage.from_("nota_grn").list() 
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error listing 'nota_grn': {e}")

    print("--- END STORAGE DEBUG ---")

except Exception as e:
    print(f"Global Error: {e}")
