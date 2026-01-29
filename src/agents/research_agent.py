from adk.agents import LLMAgent
from adk.core import AgentContext
from tools.mock_tools import MockTools
from tools.search_tool import SearchTool

class ResearcherAgent(LLMAgent):
    def __init__(self, context: AgentContext):
        super().__init__(
            name="ResearcherAgent", 
            context=context, 
            persona="""You are a Professional Researcher Agent. Your mission is to gather deep-dive facts, reliable statistics, and authoritative references.
            
            OUTPUT RULES:
            - Return ONLY the research summary.
            - Do NOT include any introductory or concluding remarks (e.g., "I found...", "Here is...").
            - Do NOT echo the "Topic" or "Context" labels.
            - Focus on identifying at least 3-5 authoritative external sources with valid URLs.
            - Structure your output with a final section: "### AUTHORITATIVE EXTERNAL LINKS" followed by a list of markdown links: [Title](URL).
            - It is better to provide a fact without a link than with a fake one.
            """,
            tools=[SearchTool.google_search]
        )
        
    def run(self, input_data: str) -> str:
        # Step 1: Extract a clean search query using the LLM
        query_extraction_prompt = f"Extract a concise Google search query to find facts/stats about: '{input_data}'. Return ONLY the query."
        search_query = super().run(query_extraction_prompt).strip().strip('"')
        self.log(f"Generated Search Query: {search_query}")
        
        # Step 2: Search
        search_results = SearchTool.google_search(search_query)
        
        # Step 3: Synthesis
        prompt = f"""Synthesize a research briefing for: {input_data}
        
        Search Findings:
        {search_results}
        
        INSTRUCTIONS:
        1. Summarize the key facts and statistics found.
        2. Identify the top 3-5 most authoritative external sources from the findings.
        3. At the end of your report, create a section "### AUTHORITATIVE EXTERNAL LINKS" and list them as [Title](URL).
        """
        return super().run(prompt)
