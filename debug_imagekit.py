
import requests
import base64

# CONFIG
PRIVATE_KEY = "private_d1MgRwtWJzF4hasu3e0ZhaC+e3Q="
API_URL = "https://api.imagekit.io/v1/files"

# PO Target (Cleaned as per JS logic)
# PO/NLD/2026/01/9727 -> GRN_PO_NLD_2026_01_9727
SEARCH_TAG = "GRN_PO_NLD_2026_01_9727" 

def search_imagekit():
    print(f"Searching ImageKit for: {SEARCH_TAG}...")
    
    # Auth: Basic Auth with Private Key (username=key, password=empty)
    auth_str = f"{PRIVATE_KEY}:"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_auth}"
    }
    
    # Advanced Search Attempt
    # We suspect the file is in a folder like "/proyek_nusantara/nota_grn" or similar.
    # ImageKit search allows 'path' and 'name'.
    
    # Try searching by name with wildcard in ALL folders
    print("Searching with wildcard query: name : *9727*")
    
    params = {
        "searchQuery": f'name : "*{SEARCH_TAG}*"', 
        # "path": "/", # Optional: restrict to folder if needed
        "limit": 100 
    }
    
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Search returned {len(data)} files.")
            for file in data:
                print(f" [MATCH] {file['name']}")
                print(f" URL: {file['url']}")
                print(f" Folder: {file['filePath']}")
                print("-" * 10)
        else:
            print(f"Search Error ({response.status_code}): {response.text}")

    except Exception as e:
        print(f"Request failed: {e}")

    # Try potential project folders
    folders = ["/proyek_nusantara", "/proyek-nusantara", "/nugrawatimaya_maker", "/default"]
    
    for f in folders:
        print(f"\nListing folder: {f} ...")
        params_f = {"path": f, "limit": 10}
        try:
             res = requests.get(API_URL, headers=headers, params=params_f)
             if res.status_code == 200:
                 data = res.json()
                 print(f"Items found: {len(data)}")
                 for item in data:
                     print(f" - {item['name']} ({item['type']})")
        except:
            pass

if __name__ == "__main__":
    search_imagekit()
