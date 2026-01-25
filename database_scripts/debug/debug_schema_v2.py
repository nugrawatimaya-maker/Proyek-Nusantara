import os
from supabase import create_client, Client

url = "https://nbpxmramqufvxiikxbve.supabase.co"
key = "sb_publishable_peLRGV8YGA5djczYBgLnkQ_buXXBknN"

print(f"Connecting to {url}")
supabase: Client = create_client(url, key)

try:
    response = supabase.table("transaksi_upah").select("*").limit(1).execute()
    if response.data:
        print("Columns in transaksi_upah:")
        for k in response.data[0].keys():
            print(f"- {k}")
    else:
        print("Table transaksi_upah is empty.")
except Exception as e:
    print(f"Error: {e}")
