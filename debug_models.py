import requests
import os

API_KEY = "AIzaSyDprUloITMwkS3E-03aF5T1Hw3qSa9Nlc4"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

try:
    response = requests.get(url)
    if response.status_code == 200:
        print("AVAILABLE MODELS:")
        models = response.json().get('models', [])
        for m in models:
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                print(f"- {m['name']}")
    else:
        print(f"Error listing models: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
