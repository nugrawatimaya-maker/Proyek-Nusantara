import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url:
    # Fallback to reading from app_config.js if env vars are missing (simplified extraction)
    config_path = os.path.join(os.path.dirname(__file__), "..", "app_config.js")
    with open(config_path, "r") as f:
        content = f.read()
        import re
        url_match = re.search(r"URL:\s*['\"](.*?)['\"]", content)
        key_match = re.search(r"KEY:\s*['\"](.*?)['\"]", content)
        if url_match: url = url_match.group(1)
        if key_match: key = key_match.group(1)

print(f"Connecting to {url}")
supabase: Client = create_client(url, key)

try:
    # Fetch 1 row to see keys
    response = supabase.table("transaksi_upah").select("*").limit(1).execute()
    if response.data:
        print("Columns in transaksi_upah:")
        print(response.data[0].keys())
    else:
        print("Table empty, checking insert error to infer schema or just guessing.")
        # Try to insert a dummy to see if valid? No, too risky.
        # Just print that it's empty.
        print("Table transaksi_upah is empty.")
except Exception as e:
    print(f"Error: {e}")
