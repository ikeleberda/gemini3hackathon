import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from adk.core import AgentContext
from adk.agents import LLMAgent

def test_fallback():
    load_dotenv()
    
    # Setup context
    context = AgentContext()
    agent = LLMAgent(name="TestAgent", context=context, persona="You are a helpful assistant.")
    
    print("--- Test 1: Invalid Primary Model, Valid Fallback ---")
    # Set an invalid primary model to force fallback
    os.environ["GOOGLE_MODEL_NAME"] = "non-existent-model"
    # Ensure a valid model is in fallback
    os.environ["GOOGLE_FALLBACK_MODELS"] = "gemini-1.5-flash, gemini-1.5-pro"
    
    result = agent.run("Tell me a short joke.")
    print(f"Result length: {len(result)}")
    
    # Check logs in context history
    print("\nLogs:")
    for log in context.history:
        print(f"  {log}")

    print("\n--- Test 2: All Models Invalid, Revert to Simulation ---")
    os.environ["GOOGLE_MODEL_NAME"] = "invalid-1"
    os.environ["GOOGLE_FALLBACK_MODELS"] = "invalid-2, invalid-3"
    
    context.history = [] # Clear history
    result = agent.run("Tell me another joke.")
    print(f"Result: {result[:100]}...")
    print(f"Is simulated: {context.is_simulated}")
    
    print("\nLogs:")
    for log in context.history:
        print(f"  {log}")

if __name__ == "__main__":
    test_fallback()
