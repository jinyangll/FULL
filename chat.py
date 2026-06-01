# pip install openai
import os
from openai import OpenAI # openai==1.81.0

client = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1"
)
 
stream = client.chat.completions.create(
    model="solar-pro3",
    messages=[
        {
            "role": "user",
            "content": "Hi, how are you?"
        }
    ],
    reasoning_effort="high", 
    stream=True,
)
 
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
 
# Use with stream=False
# print(stream.choices[0].message.content)