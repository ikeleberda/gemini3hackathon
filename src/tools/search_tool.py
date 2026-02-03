import os
import requests
from typing import List, Dict

class SearchTool:
    @staticmethod
    def google_search(query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """
        Perform a Google Custom Search.
        Requires GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_CX in env.
        """
        api_key = os.environ.get("GOOGLE_SEARCH_API_KEY")
        cx = os.environ.get("GOOGLE_SEARCH_CX")

        if not api_key or not cx:
            print("[SearchTool] Missing API Key or CX, falling back to mock.")
            return [{"title": f"Mock Result for {query}", "snippet": f"This is a simulated result for the query: '{query}'. It provides relevant background information and simulated facts to allow the content workflow to proceed without an active Google Search configuration."}]

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cx,
            "q": query,
            "num": num_results
        }

        try:
            print(f"  -> Tool Call: google_search('{query}')")
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            from tools.link_validator_tool import LinkValidatorTool
            
            results = []
            if "items" in data:
                for item in data["items"]:
                    link = item.get("link")
                    if link and LinkValidatorTool.is_link_valid(link):
                        results.append({
                            "title": item.get("title"),
                            "link": link,
                            "snippet": item.get("snippet")
                        })
                    elif link:
                        print(f"  -> LinkValidator: Filtering dead link: {link}")
            return results
        except Exception as e:
            print(f"[SearchTool] Error: {e}")
            return [{"title": "Error", "snippet": str(e)}]
