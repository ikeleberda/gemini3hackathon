import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Emulate the parsing logic from PublisherAgent to verify it
input_data = """---SEO_DATA---
Meta Title: Test Title
Meta Description: Test Desc
Slug: test-slug
---ARTICLE---
# Main Content
This is the body.
---VALIDATED_LINKS_FOR_REFERENCE_ONLY---
EXTERNAL:
- [Google](https://google.com)
"""

print("Testing Parsing Logic...")
content = input_data
seo_meta = {}

if "---SEO_DATA---" in content:
    parts = content.split("---ARTICLE---")
    seo_part = parts[0].replace("---SEO_DATA---", "").strip()
    for line in seo_part.split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            seo_meta[k.strip().lower()] = v.strip()
    if len(parts) > 1:
        content = parts[1].strip()

# Cleanup
if "---VALIDATED_LINKS_FOR_REFERENCE_ONLY---" in content:
    content = content.split("---VALIDATED_LINKS_FOR_REFERENCE_ONLY---")[0].strip()

print(f"Meta: {seo_meta}")
print(f"Content: '{content}'")

if seo_meta.get("meta title") == "Test Title" and "---VALIDATED_LINKS" not in content and "# Main Content" in content:
    print("SUCCESS: Parsing works.")
else:
    print("FAILED: Parsing logic incorrect.")
