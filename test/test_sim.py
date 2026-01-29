import os
import sys
from dotenv import load_dotenv

# Ensure src is in python path
sys.path.append(os.path.join(os.getcwd(), "src"))

from adk.core import AgentContext
from agents.seo_agent import SEOAgent
from agents.publisher_agent import PublisherAgent

def test_simulation_flow():
    load_dotenv()
    
    # Force use of simulation by removing API key if present locally
    os.environ["GOOGLE_API_KEY"] = "" # Empty to force simulation in this process
    
    context = AgentContext()
    seo_agent = SEOAgent(context)
    publisher_agent = PublisherAgent(context)
    
    topic = "Test Topic for Categories"
    print(f"1. Running SEOAgent (simulation) for topic: {topic}")
    
    # SEOAgent.run will call _simulate_llm_response in agents.py
    seo_output = seo_agent.run(topic)
    print("\n--- SEO Output ---")
    print(seo_output)
    print("--- End SEO Output ---\n")
    
    # Check if Category and Tags are in the output (they SHOULD be after my agents.py edit)
    # Wait, I failed the agents.py edit. Let me check if I actually succeeded or failed.
    # I failed it 3 times. Let me try to edit it one more time before running the test.
    
    if "Category:" in seo_output and "Tags:" in seo_output:
        print("SUCCESS: Category and Tags found in simulation output.")
    else:
        print("FAILURE: Category or Tags missing from simulation output.")

if __name__ == "__main__":
    test_simulation_flow()
