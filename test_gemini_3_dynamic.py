import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
project = os.environ.get("GCP_PROJECT_ID")
location = os.environ.get("GCP_LOCATION", "us-central1")

print(f"Project: {project}")
print(f"Location: {location}")

try:
    client = genai.Client(vertexai=True, project=project, location=location)
    
    # List models to find the exact name
    models = [m.name for m in client.models.list()]
    target = "publishers/google/models/gemini-3-pro-preview"
    
    if target in models:
        print(f"Found {target} in model list.")
        # Try using it as is
        print(f"Attempting generation with {target}...")
        response = client.models.generate_content(
            model=target,
            contents="Say hi."
        )
        print(f"Success! {response.text}")
    else:
        print(f"Could not find {target} in list. Available 'gemini-3' models:")
        for m in models:
            if "gemini-3" in m:
                print(f" - {m}")

except Exception as e:
    print(f"Error: {e}")
