import os
import sys
from dotenv import load_dotenv

# Ensure src is in python path
sys.path.append(os.path.join(os.getcwd(), "src"))

from tools.wordpress_tool import WordPressTool

def test_terms():
    load_dotenv()
    
    auth = {
        "url": os.environ.get("WP_URL"),
        "username": os.environ.get("WP_USERNAME"),
        "password": os.environ.get("WP_APP_PASSWORD")
    }
    
    if not auth["url"] or not auth["username"] or not auth["password"]:
        print("Missing WordPress credentials in .env")
        return

    print(f"Testing with URL: {auth['url']}")
    
    # Test Category
    cat_name = "Test Category " + os.urandom(2).hex()
    print(f"\n1. Creating new category: {cat_name}")
    cat_id = WordPressTool.get_or_create_term(cat_name, "categories", auth)
    print(f"Result ID: {cat_id}")
    
    print(f"\n2. Getting existing category: {cat_name}")
    cat_id_2 = WordPressTool.get_or_create_term(cat_name, "categories", auth)
    print(f"Result ID: {cat_id_2}")
    
    if cat_id == cat_id_2:
        print("SUCCESS: Category retrieval works.")
    else:
        print("FAILURE: Category retrieval failed.")

    # Test Tag
    tag_name = "Test Tag " + os.urandom(2).hex()
    print(f"\n3. Creating new tag: {tag_name}")
    tag_id = WordPressTool.get_or_create_term(tag_name, "tags", auth)
    print(f"Result ID: {tag_id}")
    
    print(f"\n4. Getting existing tag: {tag_name}")
    tag_id_2 = WordPressTool.get_or_create_term(tag_name, "tags", auth)
    print(f"Result ID: {tag_id_2}")
    
    if tag_id == tag_id_2:
        print("SUCCESS: Tag retrieval works.")
    else:
        print("FAILURE: Tag retrieval failed.")

if __name__ == "__main__":
    test_terms()
