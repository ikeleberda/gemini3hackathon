import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
env_key = os.environ.get("GOOGLE_SEARCH_API_KEY")
print(f"DEBUG: GOOGLE_SEARCH_API_KEY present? {bool(env_key)}")
if env_key:
    print(f"DEBUG: Key length: {len(env_key)}")

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from adk.core import AgentContext
from agents.manager_agent import ManagerAgent

def main():
    print("Initializing Multi-Agent Content System (Google ADK Style)...")
    
    # Create shared context
    context = AgentContext()
    
    # Initialize the Manager
    manager = ManagerAgent(context)
    
    # Check for topic in environment variable first (preferred for stability)
    initial_input = os.environ.get("AGENT_TOPIC")
    
    if initial_input:
        print(f"Received Input Topic via Env: {initial_input}")
    elif len(sys.argv) > 1:
        try:
            import json
            # Try to parse first arg as JSON
            input_data = json.loads(sys.argv[1])
            initial_input = input_data.get("topic", "Agentic AI")
            print(f"Received Input Topic via CLI JSON: {initial_input}")
        except json.JSONDecodeError:
            # Fallback to simple string
            initial_input = sys.argv[1]
            print(f"Received Input String via CLI: {initial_input}")
    
    if not initial_input:
        initial_input = "Agentic AI"

    # Final cleanup: if it somehow still looks like JSON, extract the topic
    if initial_input.startswith('{') and '"topic"' in initial_input:
        try:
            import json
            initial_input = json.loads(initial_input).get("topic", initial_input)
            print(f"Cleaned JSON from input string: {initial_input}")
        except:
            pass

    print(f"\nStarting workflow with seed topic: '{initial_input}'\n" + "="*50)
    result = manager.run(initial_input)
    
    print("="*50 + "\nWorkflow Finished!")
    print("\nFinal Output:")
    print(result)

if __name__ == "__main__":
    main()
