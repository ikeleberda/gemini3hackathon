import requests
import typing

class LinkValidatorTool:
    @staticmethod
    def is_link_valid(url: str, timeout: int = 5) -> bool:
        """
        Check if a URL is valid (returns 200 OK).
        Uses a HEAD request first for efficiency, falls back to GET if HEAD is not allowed.
        """
        if not url or not url.startswith("http"):
            return False
            
        # Blacklist common example/mock domains
        mock_domains = ["example.com", "example.org", "example.net", "mock.com", "test.com", "yourdomain.com"]
        if any(domain in url.lower() for domain in mock_domains):
            return False
            
        try:
            # Disable SSL verification warnings for user's site issues
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # Skip HEAD if we want to be thorough about soft 404s, 
            # but for performance we can keep it and just be aware of the limitation.
            # However, "pages not found" is the priority.
            
            # Use GET with stream=True to avoid downloading large files, but allowing content check
            response = requests.get(url, timeout=timeout, allow_redirects=True, stream=True, verify=False, headers=headers)
            
            # Accept 200 (OK) and 403 (Forbidden - likely anti-bot, but link exists)
            # We strictly reject 404 (Not Found) and 5xx (Server Errors)
            if response.status_code not in [200, 403]:
                return False
                
            # Content-based 404 detection (soft 404s)
            # Only check for small HTML responses to avoid performance hits
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' in content_type:
                # Read more of the content to find soft 404 indicators
                # Some sites have the error message further down
                content_chunks = []
                try:
                    for i, chunk in enumerate(response.iter_content(chunk_size=2048)):
                        content_chunks.append(chunk.decode('utf-8', errors='ignore').lower())
                        if i >= 2: # Check up to ~6KB of content
                            break
                except:
                    pass
                
                full_text = "".join(content_chunks)
                
                error_keywords = [
                    "404 not found", "page not found", "doesn't exist", "can't be found", 
                    "404 - ", "error 404", "sorry, the page you requested", "404: page not found"
                ]
                if any(kw in full_text for kw in error_keywords):
                    return False
            
            return True
        except Exception as e:
            return False
