import os
import sys
import re
import requests
from unittest.mock import MagicMock, patch

# Ensure src is in python path
sys.path.append(os.path.join(os.getcwd(), "src"))

from tools.link_validator_tool import LinkValidatorTool
from agents.research_agent import ResearcherAgent
from adk.core import AgentContext

def test_link_validator_basic():
    print("Testing LinkValidatorTool...")
    # Valid link
    assert LinkValidatorTool.is_link_valid("https://www.google.com") == True
    # Missing/Invalid link
    assert LinkValidatorTool.is_link_valid("https://this-domain-does-not-exist-12345.com") == False
    # Mock domain
    assert LinkValidatorTool.is_link_valid("https://example.com") == False
    print("LinkValidatorTool basic tests passed!")

def test_researcher_agent_validation():
    print("\nTesting ResearcherAgent post-generation link validation...")
    context = AgentContext()
    agent = ResearcherAgent(context)
    
    # Mock LLM response with a mix of valid and invalid links
    raw_briefing = """Research Findings:
Here are some facts about the Dead Link.

### AUTHORITATIVE EXTERNAL LINKS
[Wikipedia](https://www.wikipedia.org)
[Dead Link Location](https://www.nonexistent-site-123456789.com)"""
    
    # Mock LinkValidatorTool.is_link_valid to return True for wikipedia and False for dead link
    with patch('tools.link_validator_tool.LinkValidatorTool.is_link_valid') as mock_valid, \
         patch('adk.agents.LLMAgent.run') as mock_run:
        
        # Super run is called twice: once for query extraction, once for briefing
        mock_run.side_effect = ["research query", raw_briefing]
        
        def side_effect(url):
            if "wikipedia.org" in url: return True
            return False
        mock_valid.side_effect = side_effect
        
        # Process the briefing through the agent's logic
        final_briefing = agent.run("some topic")
        
        print(f"Final Briefing:\n{final_briefing}")
        
        assert "wikipedia" in final_briefing.lower()
        assert "nonexistent-site" not in final_briefing
        assert "dead link" in final_briefing.lower()
        print("ResearcherAgent link verification test passed!")

def test_search_tool_filtering():
    print("\nTesting SearchTool filtering...")
    from tools.search_tool import SearchTool
    with patch('requests.get') as mock_get, \
         patch('tools.link_validator_tool.LinkValidatorTool.is_link_valid') as mock_valid, \
         patch.dict('os.environ', {'GOOGLE_SEARCH_API_KEY': 'fake', 'GOOGLE_SEARCH_CX': 'fake'}):
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {"title": "Valid", "link": "https://www.google.com", "snippet": "valid"},
                {"title": "Invalid", "link": "https://example.com", "snippet": "invalid"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        def side_effect(url):
            if "google.com" in url: return True
            return False
        mock_valid.side_effect = side_effect
        
        results = SearchTool.google_search("test query")
        print(f"Search results: {results}")
        assert len(results) == 1
        assert results[0]['link'] == "https://www.google.com"
        print("SearchTool filtering test passed!")

def test_soft_404_detection():
    print("\nTesting soft 404 detection...")
    # This is harder to test without a real server, but we can mock the response
    with patch('requests.head') as mock_head, patch('requests.get') as mock_get:
        # Mock HEAD to return 200
        mock_head.return_value.status_code = 200
        
        # Mock GET to return a soft 404 page with the error further down
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.headers = {'Content-Type': 'text/html'}
        # Give it a few chunks to test the loop
        mock_get_response.iter_content.return_value = [
            b"<html><head><title>Some Title</title></head><body>"
            b"<div>Welcome to our site.</div>"
            b"<div>404 not found: The requested URL was not found on this server.</div>"
            b"</body></html>"
        ]
        mock_get.return_value = mock_get_response
        
        is_valid = LinkValidatorTool.is_link_valid("https://some-site.com/broken")
        print(f"Is soft 404 valid? {is_valid}")
        print(f"Response status: {mock_get_response.status_code}")
        print(f"Response content type: {mock_get_response.headers.get('Content-Type')}")
        assert is_valid == False
        print("Soft 404 detection test passed!")

if __name__ == "__main__":
    try:
        test_link_validator_basic()
        test_researcher_agent_validation()
        test_search_tool_filtering()
        test_soft_404_detection()
        print("\nAll reproduction tests completed successfully!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nTests failed: {e}")
        sys.exit(1)
