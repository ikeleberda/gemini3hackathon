from adk.agents import LLMAgent
from adk.core import AgentContext

class SEOAgent(LLMAgent):
    def __init__(self, context: AgentContext):
        super().__init__(
            name="SEOAgent", 
            context=context, 
            persona="""You are a Professional SEO Specialist. Your task is to optimize the article while maintaining a strict output format.
            
            OUTPUT RULES:
            - Return ONLY the optimized data using the separators below.
            - Do NOT include any introductory or concluding meta-commentary.
            - Ensure all internal/external links are NATURALLY EMBEDDED within the article text using Markdown anchor text (e.g., [descriptive text](URL)).
            - DO NOT append a list of links at the end of the article text.
            - The article must read like a cohesive piece with links integrated into the narrative.
            - Ensure all internal/external links are accurately placed with descriptive anchor text.
            
            FORMAT REQUIRED:
            ---SEO_DATA---
            Meta Title: [Title]
            Meta Description: [Description]
            Slug: [Slug]
            OG Title: [Title]
            OG Description: [Description]
            Canonical: [URL or empty]
            Category: [Primary Category Name]
            Tags: [Comma, Separated, Tags]
            JSON-LD: [Valid JSON-LD object]
            ---ARTICLE---
            # [Main Heading]
            [Optimized Article Content]

            ### OPTIMIZATION RULES:
            1. Metadata: Title (<60 chars), Description (150-160 chars).
            2. Category/Tags: Choose 1 relevant primary Category and 3-5 specific Tags based on the content.
            3. Structure: Single H1, logical H2/H3 nesting.
            3. Keywords: Natural placement in H1 and first 100 words.
            4. Linking: 1-2 Internal links provided below. 1-2 authoritative External links (ONLY use/verify the links already present in the article draft provided by the Writer). YOU MUST ENSURE THAT AT LEAST ONE AUTHORITATIVE EXTERNAL LINK IS PRESENT IN THE FINAL CONTENT. You are strictly forbidden from inventing or guessing any URLs.
            5. Alt Text: Ensure <img> tags have descriptive alt text.
            """,
            tools=[]
        )

    def run(self, input_data: str) -> str:
        self.log("Starting link optimization and verification...")
        
        import os
        import re
        from tools.wordpress_tool import WordPressTool
        from tools.link_validator_tool import LinkValidatorTool
        
        wp_auth = {
            "url": os.environ.get("WP_URL"),
            "username": os.environ.get("WP_USERNAME"),
            "password": os.environ.get("WP_APP_PASSWORD")
        }
        
        # 1. Fetch and validate internal links
        recent_posts = []
        try:
            self.log("Fetching recent posts for internal linking...")
            raw_posts = WordPressTool.get_recent_posts(wp_auth, count=5)
            for p in raw_posts:
                if LinkValidatorTool.is_link_valid(p['link']):
                    recent_posts.append(p)
                else:
                    self.log(f"LinkValidator: Filtering dead internal link: {p['link']}")
        except Exception as e:
            self.log(f"Warning: Could not fetch recent posts: {e}")

        # 2. Extract and validate external links from the draft
        # Regex to find markdown links: [text](url)
        found_links = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', input_data)
        external_links = []
        for text, url in found_links:
            # Check if it's external (not the WP site)
            wp_site_url = os.environ.get("WP_URL", "")
            if wp_site_url and wp_site_url in url:
                continue
            
            self.log(f"Validating external link: {url}")
            if LinkValidatorTool.is_link_valid(url):
                external_links.append({"text": text, "url": url})
            else:
                self.log(f"LinkValidator: Filtering dead external link: {url}")

        # 3. Build context for the LLM
        links_context = ""
        if recent_posts:
            links_context += "VALID INTERNAL LINKS (Use 1-2):\n"
            links_context += "\n".join([f"- [{p['title']}]({p['link']})" for p in recent_posts]) + "\n\n"
        
        if external_links:
            links_context += "VALID EXTERNAL LINKS (Keep these if relevant):\n"
            links_context += "\n".join([f"- [{l['text']}]({l['url']})" for l in external_links]) + "\n"
        
        if not links_context:
            links_context = "No validated internal or external links found."
            linking_rule = "4. Linking: No validated links provided. Focus on content quality and metadata. Do NOT add any links."
        else:
            linking_rule = "4. Linking: Use a mix of the validated Internal and External links provided below. YOU MUST EMBED THESE LINKS NATURALLY WITHIN THE ARTICLE TEXT. Do NOT list them at the end. Use descriptive anchor text for each link. You are strictly forbidden from inventing or guessing any URLs not listed below."

        # 4. Update persona and run
        enhanced_persona = self.persona.replace(
            "4. Linking: 1-2 Internal links provided below. 1-2 authoritative External links (ONLY use/verify the links already present in the article draft provided by the Writer). You are strictly forbidden from inventing or guessing any URLs.",
            linking_rule
        )
        enhanced_persona += f"\n\n--- VALIDATED LINKS TO USE ---\n{links_context}"
        
        original_persona = self.persona
        self.persona = enhanced_persona
        result = super().run(input_data)
        self.persona = original_persona
        
        # 5. Append validated links section for PublisherAgent (this will be stripped before publishing)
        if recent_posts or external_links:
            result += "\n\n---VALIDATED_LINKS_FOR_REFERENCE_ONLY---\n"
            if recent_posts:
                result += "INTERNAL:\n"
                result += "\n".join([f"- [{p['title']}]({p['link']})" for p in recent_posts]) + "\n"
            if external_links:
                result += "EXTERNAL:\n"
                result += "\n".join([f"- [{l['text']}]({l['url']})" for l in external_links]) + "\n"
        
        return result
