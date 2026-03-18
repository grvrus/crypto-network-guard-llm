import os
from dotenv import load_dotenv
import cohere

load_dotenv()

api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    raise ValueError("COHERE_API_KEY not found in .env")

co = cohere.ClientV2(api_key)

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: Cohere works"
        }
    ]
)

print(response.message.content[0].text)