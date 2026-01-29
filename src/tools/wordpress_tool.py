import requests
from typing import Dict
import base64

class WordPressTool:
    @staticmethod
    def upload_media(file_path: str, auth: Dict) -> Dict:
        """
        Upload an image to WordPress Media Library.
        Returns a dict with 'id' (int) and 'link' (str) or None if failed.
        """
        wp_url = auth.get("url")
        username = auth.get("username")
        password = auth.get("password")

        if not wp_url or not username or not password:
            print("[WordPressTool] Missing URL or credentials for upload.")
            return None

        import os
        if not os.path.exists(file_path):
            print(f"[WordPressTool] File not found: {file_path}")
            return None

        # Endpoint
        base_url = wp_url.rstrip("/")
        api_endpoint = f"{base_url}/wp-json/wp/v2/media"

        # Auth
        credentials = f"{username}:{password}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        
        # Headers - Content-Disposition is critical
        filename = os.path.basename(file_path)
        headers = {
            "Authorization": f"Basic {token}",
            "Content-Disposition": f'attachment; filename="{filename}"',
        }
        
        # Determine mime type
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "image/png" # Default
            
        headers["Content-Type"] = mime_type

        try:
            print(f"  -> Tool Call: Uploading media {filename}...")
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            with open(file_path, "rb") as f:
                image_data = f.read()
                
            response = requests.post(api_endpoint, data=image_data, headers=headers, verify=False)
            
            if response.status_code == 201:
                media_data = response.json()
                media_id = media_data.get("id")
                media_link = media_data.get("source_url")
                print(f"  -> SUCCESS: Media uploaded. ID: {media_id}, Link: {media_link}")
                return {"id": media_id, "link": media_link}
            else:
                print(f"  -> ERROR: Failed to upload media. Status: {response.status_code}")
                print(f"  -> Response: {response.text[:200]}...")
                return None
                
        except Exception as e:
            print(f"  -> ERROR: Exception during media upload: {e}")
            return None

    @staticmethod
    def get_or_create_term(name: str, taxonomy: str, auth: Dict) -> int:
        """
        Get term ID by name or create it if missing.
        Taxonomy can be 'categories' or 'tags'.
        """
        wp_url = auth.get("url")
        username = auth.get("username")
        password = auth.get("password")
        
        base_url = wp_url.rstrip("/")
        api_endpoint = f"{base_url}/wp-json/wp/v2/{taxonomy}"
        
        credentials = f"{username}:{password}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json"
        }
        
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 1. Search for existing term
        try:
            search_params = {"search": name}
            # Also verify exact match because search is fuzzy
            response = requests.get(api_endpoint, params=search_params, headers=headers, verify=False)
            if response.status_code == 200:
                terms = response.json()
                name_clean = name.strip().lower()
                for term in terms:
                    if term["name"].strip().lower() == name_clean:
                        return term["id"]
        except Exception as e:
            print(f"  -> ERROR: Failed to search {taxonomy}: {e}")

        # 2. Create if not found
        try:
            print(f"  -> Creating new {taxonomy}: {name}")
            data = {"name": name}
            response = requests.post(api_endpoint, json=data, headers=headers, verify=False)
            if response.status_code == 201:
                return response.json().get("id")
            else:
                print(f"  -> ERROR: Failed to create {taxonomy}. Status: {response.status_code}")
                return None
        except Exception as e:
            print(f"  -> ERROR: Failed to create {taxonomy}: {e}")
            return None

    @staticmethod
    def publish_post(title: str, content: str, auth: Dict, featured_media_id: int = None, slug: str = None, excerpt: str = None, categories: list = None, tags: list = None, status: str = "publish") -> str:
        """
        Publish a post to WordPress using Basic Auth.
        auth dict must contain: 'url', 'username', 'password'
        status can be 'publish', 'draft', 'private', etc.
        """
        wp_url = auth.get("url")
        username = auth.get("username")
        password = auth.get("password")

        if not wp_url or not username or not password:
            print("[WordPressTool] Missing URL or credentials.")
            return "FAILED: Missing Credentials"

        # Construct API Endpoint
        base_url = wp_url.rstrip("/")
        api_endpoint = f"{base_url}/wp-json/wp/v2/posts"

        # Create Basic Auth Header
        credentials = f"{username}:{password}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json"
        }

        data = {
            "title": title,
            "content": content,
            "status": status 
        }
        
        if slug:
            data["slug"] = slug
        if excerpt:
            data["excerpt"] = excerpt
        
        if featured_media_id:
            data["featured_media"] = featured_media_id
        if categories:
            data["categories"] = categories
        if tags:
            data["tags"] = tags

        try:
            print(f"  -> Tool Call: Publishing to {api_endpoint}...")
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = requests.post(api_endpoint, json=data, headers=headers, verify=False)
            
            if response.status_code == 201:
                post_data = response.json()
                link = post_data.get("link")
                post_slug = post_data.get("slug")
                
                # WordPress sometimes returns ?p=ID format instead of pretty permalink
                # Construct the pretty URL from the slug if available
                if link and "?p=" in link and post_slug:
                    # Build pretty permalink from base URL and slug
                    from datetime import datetime
                    now = datetime.now()
                    pretty_link = f"{base_url}/{now.year}/{now.month:02d}/{now.day:02d}/{post_slug}/"
                    print(f"  -> SUCCESS: Post published at {pretty_link} (converted from {link})")
                    return pretty_link
                else:
                    print(f"  -> SUCCESS: Post published at {link}")
                    return link
            else:
                print(f"  -> ERROR: Failed to publish. Status: {response.status_code}")
                return f"FAILED: API Error {response.status_code}"

        except Exception as e:
            print(f"  -> ERROR: Exception during publish: {e}")
            return f"FAILED: {str(e)}"

    @staticmethod
    def get_recent_posts(auth: Dict, count: int = 10) -> list:
        """
        Fetch recent posts from WordPress.
        Returns a list of dictionaries with 'title' and 'link'.
        """
        wp_url = auth.get("url")
        username = auth.get("username")
        password = auth.get("password")

        if not wp_url or not username or not password:
            print("[WordPressTool] Missing URL or credentials for fetching.")
            return []

        base_url = wp_url.rstrip("/")
        api_endpoint = f"{base_url}/wp-json/wp/v2/posts?per_page={count}&_fields=title,link"

        credentials = f"{username}:{password}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        headers = {
            "Authorization": f"Basic {token}",
        }

        try:
            print(f"  -> Tool Call: Fetching recent posts from {api_endpoint}...")
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = requests.get(api_endpoint, headers=headers, verify=False)
            if response.status_code == 200:
                posts = response.json()
                return [{"title": p["title"]["rendered"], "link": p["link"]} for p in posts]
            return []
        except Exception as e:
            print(f"  -> ERROR: Exception during fetching posts: {e}")
            return []

