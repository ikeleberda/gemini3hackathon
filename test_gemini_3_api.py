import os
import sys
from google import genai
from dotenv import load_dotenv

# Force output to stdout for run_command
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

print(f"DEBUG: API Key length: {len(api_key) if api_key else 0}")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
else:
    try:
        # Explicitly NOT using Vertex AI
        client = genai.Client(api_key=api_key)
        model_name = "gemini-3-pro-preview"
        print(f"Testing Gemini 3 Pro ({model_name}) via API Key...")
        response = client.models.generate_content(
            model=model_name,
            contents="Say hello from Gemini 3 Pro via API Key!"
        )
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
