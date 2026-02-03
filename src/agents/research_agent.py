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
        raw_briefing = super().run(prompt)
        
        self.log("Validating links in research briefing...")
        import re
        from tools.link_validator_tool import LinkValidatorTool
        
        # Regex to find markdown links: [text](url)
        found_links = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', raw_briefing)
        
        valid_links_section = "\n### AUTHORITATIVE EXTERNAL LINKS\n"
        has_valid_links = False
        
        # Verify each link found in the briefing
        unique_urls = set()
        for text, url in found_links:
            if url in unique_urls:
                continue
            
            self.log(f"Researcher validation: {url}")
            if LinkValidatorTool.is_link_valid(url):
                valid_links_section += f"- [{text}]({url})\n"
                has_valid_links = True
                unique_urls.add(url)
            else:
                self.log(f"Researcher filtering dead link: {url}")
                # Remove the dead link from the main text if it appears as a markdown link
                raw_briefing = raw_briefing.replace(f"[{text}]({url})", text)
        
        # Split the briefing at the links section and rebuild it with only valid links
        if "### AUTHORITATIVE EXTERNAL LINKS" in raw_briefing:
            main_content = raw_briefing.split("### AUTHORITATIVE EXTERNAL LINKS")[0].strip()
        else:
            main_content = raw_briefing.strip()
            
        if has_valid_links:
            return f"{main_content}\n{valid_links_section}"
        else:
            return main_content
