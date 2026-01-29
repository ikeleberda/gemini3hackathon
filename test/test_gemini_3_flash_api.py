import os
import sys
from google import genai
from dotenv import load_dotenv

# Force output to stdout for run_command
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
else:
    try:
        client = genai.Client(api_key=api_key)
        model_name = "gemini-3-flash-preview"
        print(f"Testing Gemini 3 Flash ({model_name}) via API Key...")
        response = client.models.generate_content(
            model=model_name,
            contents="Say hello from Gemini 3 Flash via API Key!"
        )
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
