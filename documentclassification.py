# pip install openai
import base64
import json
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1/document-classification"
)
 
def encode_img_to_base64(img_path):
    with open(img_path, 'rb') as img_file:
        img_bytes = img_file.read()
        base64_data = base64.b64encode(img_bytes).decode('utf-8')
        return base64_data
 
filepath = "./your_document.png"
base64_data = encode_img_to_base64(filepath)
 
response = client.chat.completions.create(
    model="document-classify",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:application/octet-stream;base64,{base64_data}"}
                }
            ]
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "document-classify",
            "schema": {
                "type": "string",
                "oneOf": [
                    {"const": "invoice", "description": "Commercial invoice with itemized charges and billing information"},
                    {"const": "receipt", "description": "Receipt showing purchase transaction details"},
                    {"const": "contract", "description": "Legal agreement or contract document"},
                    {"const": "cv", "description": "Curriculum vitae or resume"},
                    {"const": "others", "description": "Other"}
                ]
            }
        }
    }
)
 
print(response) 