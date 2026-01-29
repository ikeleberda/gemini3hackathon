from typing import List, Dict

class MockTools:
    @staticmethod
    def search_web(query: str) -> List[Dict[str, str]]:
        """Simulate a web search."""
        print(f"  -> Tool Call: search_web('{query}')")
        return [
            {"title": f"Result for {query} 1", "snippet": "Detailed info about " + query},
            {"title": f"Result for {query} 2", "snippet": "More stats and facts regarding " + query}
        ]

    @staticmethod
    def generate_image(prompt: str) -> str:
        """Simulate image generation."""
        print(f"  -> Tool Call: generate_image('{prompt}')")
        return f"image_generated_based_on_{prompt[:10].replace(' ', '_')}.png"

    @staticmethod
    def publish_content(title: str, content: str, meta: Dict, auth: Dict = None) -> str:
        """Simulate publishing to WordPress with auth check."""
        if not auth:
             print("  -> [WARNING] No credentials provided for WordPress!")
             return "FAILED: Missing Credentials"
        
        username = auth.get("username")
        url = auth.get("url")
        
        if not username or not url:
             print("  -> [WARNING] Incomplete credentials provided.")
             return "FAILED: Invalid Credentials"

        print(f"  -> Tool Call: publish_content('{title}') to {url} as {username}")
        return "https://wordpress.example.com/new-post-123"
