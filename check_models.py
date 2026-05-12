"""Run this to verify your Groq API key works."""
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Say hello in one word."}],
    max_tokens=10
)
print("SUCCESS:", response.choices[0].message.content)
