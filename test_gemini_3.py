import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
project = os.environ.get("GCP_PROJECT_ID")
location = os.environ.get("GCP_LOCATION", "us-central1")
use_vertex = os.environ.get("USE_VERTEX_AI", "").lower() == "true"

print(f"Project: {project}")
print(f"Location: {location}")
print(f"Use Vertex: {use_vertex}")

try:
    if use_vertex:
        client = genai.Client(vertexai=True, project=project, location=location)
    else:
        api_key = os.environ.get("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)

    model_name = "publishers/google/models/gemini-3-flash-preview"
    print(f"Testing model: {model_name}")
    response = client.models.generate_content(
        model=model_name,
        contents="Say hello from Gemini 3 Flash!"
    )
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
