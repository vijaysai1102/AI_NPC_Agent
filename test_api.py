"""Diagnostic script — run this to see the exact API error."""
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "")
print(f"Key loaded: {api_key[:12]}...")

# Check which packages are installed
try:
    from google import genai
    print("google-genai SDK: OK")
except ImportError:
    print("ERROR: google-genai not installed. Run: pip install google-genai")
    exit(1)

client = genai.Client(api_key=api_key)

print("\nTesting generate_content with gemini-2.0-flash-lite ...")
try:
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents="Say the word hello."
    )
    print("SUCCESS:", response.text)
except Exception as e:
    print(f"\nERROR TYPE : {type(e).__name__}")
    print(f"ERROR MSG  : {e}")
