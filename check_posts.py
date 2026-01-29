import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

wp_url = os.environ.get("WP_URL")
username = os.environ.get("WP_USERNAME")
password = os.environ.get("WP_APP_PASSWORD")

if not wp_url: 
    print("No WP credentials.")
    exit()

creds = f"{username}:{password}"
token = base64.b64encode(creds.encode()).decode('utf-8')
headers = {"Authorization": f"Basic {token}"}

# Get posts (any status)
endpoint = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts?status=publish,draft&per_page=5"

try:
    import urllib3
    urllib3.disable_warnings()
    r = requests.get(endpoint, headers=headers, verify=False)
    if r.status_code == 200:
        posts = r.json()
        print(f"Found {len(posts)} recent posts:")
        for p in posts:
            print(f"- {p['title']['rendered']} (Status: {p['status']}) - {p['link']}")
    else:
        print(f"Failed to fetch posts: {r.status_code} {r.text}")
except Exception as e:
    print(f"Error: {e}")
