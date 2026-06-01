# pip install requests

import os
import requests

api_key = os.getenv("UPSTAGE_API_KEY")  # ex: up_xxxYYYzzzAAAbbbCCC
filename = "YOUR_FILE_NAME"  # ex: ./image.png
 
url = "https://api.upstage.ai/v1/document-digitization"
headers = {"Authorization": f"Bearer {api_key}"}
files = {"document": open(filename, "rb")}
data = {"ocr": "force", "base64_encoding": "['table']", "model": "document-parse"}
response = requests.post(url, headers=headers, files=files, data=data)
 
print(response.json())