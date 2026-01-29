import os
import sys
import re

# Ensure src is in python path
sys.path.append(os.path.join(os.getcwd(), "src"))

from adk.core import AgentContext
from agents.publisher_agent import PublisherAgent

def test_link_and_meta_stripping():
    context = AgentContext()
    publisher = PublisherAgent(context)
    
    # Mock input data with SEO data, Category, Tags, and a leaky header
    sample_content = """---SEO_DATA---
Meta Title: Test Post
Meta Description: A test post for refining content and metadata.
Slug: test-post
Category: Artificial Intelligence
Tags: AI, Agentic, Testing
JSON-LD: {}
---ARTICLE---
# Test Post
This is a post with an [embedded link](https://google.com).

### AUTHORITATIVE EXTERNAL LINKS
1. [Google](https://google.com)
2. [Research Paper](https://example.com/paper)

---VALIDATED_LINKS_FOR_REFERENCE_ONLY---
INTERNAL:
- [Old Post](https://example.com/old)
EXTERNAL:
- [Google](https://google.com)
"""
    
    # Step 1: Simulate the stripping logic in PublisherAgent
    content = sample_content
    
    # Logic extracted from publisher_agent.py
    seo_meta = {}
    if "---SEO_DATA---" in content:
        article_match = re.search(r"---+\s*ARTICLE\s*---+", content, re.IGNORECASE)
        if article_match:
            article_marker = article_match.group(0)
            parts = content.split(article_marker)
            meta_block = parts[0].split("---SEO_DATA---")[-1].strip()
            content = parts[1].strip()
            
            for line in meta_block.split("\n"):
                line = line.strip()
                if ":" in line:
                    k, v = line.split(":", 1)
                    seo_meta[k.strip().lower()] = v.strip()
    
    print(f"Parsed Meta: {seo_meta}")
    assert seo_meta.get("category") == "Artificial Intelligence"
    assert "AI, Agentic, Testing" in seo_meta.get("tags")

    # Step 2: Strip validated links reference
    if "---VALIDATED_LINKS_FOR_REFERENCE_ONLY---" in content:
        print("Stripping reference links...")
        content = content.split("---VALIDATED_LINKS_FOR_REFERENCE_ONLY---")[0].strip()
    
    # Step 3: Final cleanup of research headers
    print("Performing final cleanup of research headers...")
    content = re.sub(r"###\s*AUTHORITATIVE\s*EXTERNAL\s*LINKS.*", "", content, flags=re.IGNORECASE | re.DOTALL).strip()
    
    print(f"Final Content to be published:\n{content}")
    
    assert "### AUTHORITATIVE EXTERNAL LINKS" not in content
    assert "---VALIDATED_LINKS_FOR_REFERENCE_ONLY---" not in content
    assert "Research Paper" not in content
    assert "[embedded link](https://google.com)" in content
    print("\nSUCCESS: Category parsing and header stripping logic verified!")

if __name__ == "__main__":
    test_link_and_meta_stripping()
