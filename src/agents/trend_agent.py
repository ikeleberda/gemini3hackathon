from adk.agents import LLMAgent
from adk.core import AgentContext
from tools.mock_tools import MockTools
from tools.search_tool import SearchTool

class TrendAgent(LLMAgent):
    def __init__(self, context: AgentContext):
        super().__init__(
            name="TrendAgent", 
            context=context, 
            persona="""You are a Trend/Ideation Specialist. Your responsibility is to provide a clean list of trending topics and high-potential keywords.
            
            OUTPUT RULES:
            - Return ONLY the list of trends/keywords.
            - Do NOT include any introductory or concluding remarks.
            - Format each trend on a new line.
            """,
            tools=[SearchTool.google_search]
        )

    def run(self, input_data: str) -> str:
        # Final safeguard: ensure input_data is a clean string, not a JSON fragment
        if isinstance(input_data, str) and input_data.startswith('{') and '"topic"' in input_data:
            try:
                import json
                input_data = json.loads(input_data).get("topic", input_data)
                self.log(f"Safeguard: Cleaned JSON from input in TrendAgent: {input_data}")
            except:
                pass
                
        # Override to add specific logic or pre/post processing if needed
        self.log(f"Scanning for trends related to: {input_data}")
        # Try real search first
        search_results = SearchTool.google_search(f"trending topics and keywords for {input_data}")
        
        # Pass search results context to the LLM
        prompt = f"Identify the top 3-5 trending topics or keywords for: {input_data}\n\nSearch Context:\n{search_results}"
        return super().run(prompt)
