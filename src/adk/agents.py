import abc
import typing
import os
from .core import BaseAgent, AgentContext

class LLMAgent(BaseAgent):
    """An agent that uses an LLM (simulated) to perform tasks."""
    
    def __init__(self, name: str, context: AgentContext, persona: str, tools: typing.List[typing.Callable] = None):
        super().__init__(name, context)
        self.persona = persona
        self.tools = tools or []

    def run(self, input_data: typing.Any) -> str:
        self.log(f"Received input: {input_data}")
        self.log(f"Thinking as {self.persona}...")
        
        # Real Gemini Integration
        api_key = self.context.google_api_key
        use_vertex = os.environ.get("USE_VERTEX_AI", "").lower() == "true"
        project = os.environ.get("GCP_PROJECT_ID")
        location = os.environ.get("GCP_LOCATION", "us-central1")

        if not api_key and not use_vertex:
            raise Exception("Missing Google API Key. Please set it in Settings.")

        if api_key or use_vertex:
            # Prepare model list: primary model first, then fallbacks
            primary_model = getattr(self.context, 'google_model_name', None) or os.environ.get("GOOGLE_MODEL_NAME", "gemini-3-flash-preview")
            fallback_str = getattr(self.context, 'google_fallback_models', None) or os.environ.get("GOOGLE_FALLBACK_MODELS", "")
            # Support both comma and pipe delimiters to avoid CLI issues
            fallback_models = [m.strip() for m in fallback_str.replace("|", ",").split(",") if m.strip()]
            
            models_to_try = [primary_model] + [m for m in fallback_models if m != primary_model]
            
            from google import genai
            if use_vertex:
                self.log(f"Using Vertex AI (Project: {project}, Location: {location})")
                client = genai.Client(vertexai=True, project=project, location=location)
            else:
                client = genai.Client(api_key=api_key)

            for model_name in models_to_try:
                try:
                    self.log(f"Attempting to use model: {model_name}")
                    # Construct a prompt that includes the persona context
                    prompt = f"""
                    You are: {self.persona}
                    
                    TASK:
                    Process the provided input and return ONLY the resulting content. 
                    Focus on the substance and structure requested.
                    
                    CRITICAL INSTRUCTIONS:
                    - Output ONLY the clean result.
                    - Do NOT echo the input headers, labels, or instruction prefixes (e.g., "Synthesize...", "Search Findings:", "Topic:").
                    - Do NOT include any introductory or concluding meta-commentary.
                    - Do NOT wrap the result in markdown code blocks.
                    
                    INPUT: 
                    {input_data}
                    
                    FINAL CONTENT:
                    """
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    output_text = response.text
                    output_text = self._clean_output(output_text)
                    self.log(f"Output ({model_name}): {output_text[:100]}...") # Log brief output
                    return output_text
                except Exception as e:
                    self.log(f"Model {model_name} failed: {e}")
                    continue # Try next model

            self.log("All configured models failed. Falling back to simulation.")

        # Fallback to simulation
        self.context.is_simulated = True
        response = self._simulate_llm_response(input_data)
        self.log(f"Output: {response}")
        return response

    def _clean_output(self, text: str) -> str:
        """Strip markdown code blocks, system headers, and multi-layered echoes."""
        text = text.strip()
        
        # Remove common agent headers/prefixes that might have leaked
        system_patterns = [
            r"RESULT:", r"FINAL CONTENT:", r"Output:", r"Research Report:", 
            r"Trend Report:", r"Synthesize.*?:", r"Search Findings:", 
            r"Comprehensive research for.*?\.", r"Topic:.*?\n",
            r"### AUTHORITATIVE EXTERNAL LINKS"
        ]
        
        import re
        for pattern in system_patterns:
            text = re.sub(f"^{pattern}", "", text, flags=re.IGNORECASE | re.MULTILINE).strip()

        # Handle cases where LLM wraps output in ```markdown or ```
        if text.startswith("```"):
            lines = text.splitlines()
            if len(lines) >= 2:
                start_idx = 1
                end_idx = len(lines)
                if lines[-1].strip() == "```":
                    end_idx = -1
                text = "\n".join(lines[start_idx:end_idx]).strip()
        
        # Extract content between backticks if it looks like a block
        if "```" in text:
            match = re.search(r"```(?:\w+)?\n?(.*?)\n?```", text, re.DOTALL)
            if match:
                text = match.group(1).strip()

        return text

    def _simulate_llm_response(self, input_data: str) -> str:
        """Simulate an LLM response based on persona and input."""
        # Use the persisted topic from context if available, otherwise fallback
        topic = self.context.topic or str(input_data).strip()
        if len(topic) > 100 or "# " in topic:
            # If we don't have a clean topic, try to extract one from input_data
            if "# " in str(input_data):
                topic = str(input_data).split("# ")[1].split("\n")[0].strip()
            else:
                topic = topic[:50] + "..."
        
        # Simple heuristic response generation for demo purposes
        if "trend" in self.name.lower():
            return f"Key Trends:\n- Rising interest in {topic} applications\n- Shift towards automated {topic} solutions\n- Emerging niche: {topic} innovation and strategy\n- Increased adoption of {topic} across diverse industries\n- Integration of {topic} with existing cloud frameworks"
        elif "research" in self.name.lower():
            return f"""Key Findings for {topic}:
1. Industry standards for {topic} are evolving rapidly to meet new market demands as of 2026.
2. 75% of surveyed professionals prefer integrated {topic} workflows over legacy systems.
3. Market leaders are doubling down on scalability and security in their {topic} implementations.
4. Recent statistics indicate a 30% growth in {topic}-related adoption in the last year.
5. Expert consensus points towards {topic} being the next major shift in technical innovation.

### AUTHORITATIVE EXTERNAL LINKS
- [{topic} Industry Report 2026](https://example.com/{topic.lower().replace(' ', '-')}-report)
- [Future of {topic} Research](https://example.com/future-of-{topic.lower().replace(' ', '-')})
- [Global {topic} Standards](https://example.com/{topic.lower().replace(' ', '-')}-standards)"""
        elif "writer" in self.name.lower():
            content = f"# The Ultimate Guide to {topic}\n\n"
            content += f"In today's rapidly evolving landscape, **{topic}** has emerged as a cornerstone of innovation and strategic growth. Whether you are a professional looking to sharpen your skills or an enthusiast eager to explore new horizons, understanding the fundamental principles of {topic} is essential for success in 2026. According to the latest [industry benchmarks](https://example.com/{topic.lower().replace(' ', '-')}-report), organizations that embrace this shift are seeing unprecedented gains.\n\n"
            content += f"## The Core Principles of {topic}\n\n"
            content += f"At its heart, {topic} is built on three main pillars: accessibility, scalability, and efficiency. By focusing on these core values, organizations can leverage {topic} to automate complex workflows and drive meaningful results. Recent data from the [Global {topic} Standards](https://example.com/{topic.lower().replace(' ', '-')}-standards) initiative suggest that early adopters of robust frameworks see as much as a 40% improvement in productivity within the first quarter of implementation.\n\n"
            content += f"Furthermore, {topic} integration allows for more seamless communication between disparate systems. This interconnectedness is a key driver in the [future of {topic} research](https://example.com/future-of-{topic.lower().replace(' ', '-')}), where experts are exploring how to further optimize these human-technical interfaces. The goal is no longer just performance, but sustainable growth.\n\n"
            content += f"## Implementation Strategies\n\n"
            content += f"Successfully implementing {topic} requires a structured approach. Start by auditing your current processes to identify bottlenecks where {topic} can provide the most immediate value. Next, invest in training and tools to ensure your team is equipped to handle the transition. Finally, maintain a continuous feedback loop to refine your application of {topic} as new trends emerge.\n\n"
            content += f"### Conclusion\n\n"
            content += f"As we look towards the future, it's clear that {topic} will continue to play a pivotal role in shaping how we work and interact with technology. By staying informed and adopting a proactive mindset, you can position yourself at the forefront of this exciting field. For more insights, keep an eye on emerging updates in the [Global {topic} Standards](https://example.com/{topic.lower().replace(' ', '-')}-standards) reports."
            return content
        elif "seo" in self.name.lower():
            article = f"# Mastering {topic}: A Comprehensive Guide for 2026\n\n"
            article += f"Mastering **{topic}** is no longer just an advantage; it's a necessity in the modern digital era. This comprehensive guide explores why {topic} is transforming industries and how you can stay ahead of the curve. As noted in the [latest industry report](https://example.com/{topic.lower().replace(' ', '-')}-report), the demand for these skills is at an all-time high.\n\n"
            article += f"## Why {topic} Matters Now\n\n"
            article += f"The rise of autonomous systems and the increasing complexity of data have made {topic} more relevant than ever. From improving customer experiences to optimizing backend operations, {topic} offers a versatile solution to modern challenges. Experts at the [Future of {topic} Research](https://example.com/future-of-{topic.lower().replace(' ', '-')}) project agree that the next decade will be defined by how effectively we integrate these protocols into our daily workflows.\n\n"
            article += f"## Best Practices for {topic}\n\n"
            article += f"When working with {topic}, it's important to keep SEO and user experience in mind. Ensure your content is authoritative, cites reliable sources like the [Global {topic} Standards](https://example.com/{topic.lower().replace(' ', '-')}-standards), and provides actionable insights. Use descriptive anchor text for any internal or external links to enhance navigation and topical relevance. By following these best practices, your content will not only rank higher but also provide genuine value to your readers.\n\n"
            article += f"### Transitioning to a {topic}-First Approach\n\n"
            article += f"The shift toward a {topic}-first mentality requires both cultural and technical changes. Organizations must be willing to experiment and iterate on their findings. As we see in the [various case studies](https://example.com/{topic.lower().replace(' ', '-')}-report), those that succeed are often those that prioritize agility over rigid hierarchies.\n\n"
            article += f"### Impact and Future Outlook\n\n"
            article += f"The future of {topic} looks incredibly promising. With advancements in AI and machine learning, we can expect {topic} to become even more intuitive and powerful. Staying curious and adaptable will be your greatest asset as you navigate the future of this field."
            
            return f"""---SEO_DATA---
Meta Title: Master {topic} | Professional Guide 2026
Meta Description: Learn everything about {topic} in our comprehensive, SEO-optimized article. Explore best practices, future trends, and implementation strategies.
Slug: mastering-{topic.lower().replace(' ', '-')}
OG Title: Mastering {topic}: The Future of Innovation
OG Description: Your one-stop resource for insights into {topic}. Expert strategies and implementation guides for 2026.
Canonical: 
Category: Technology
Tags: {topic}, AI, Automation, Strategy, 2026
JSON-LD: {{}}
---ARTICLE---
{article}
"""
        elif "media" in self.name.lower():
            return f"A vibrant conceptual illustration representing {topic} in a modern workspace."
        elif "publisher" in self.name.lower():
            return f"Published successfully."
        
        return f"Finalized {input_data} as {self.name}."

class WorkflowAgent(BaseAgent):
    """An agent that coordinates other agents."""
    
    def __init__(self, name: str, context: AgentContext, sub_agents: typing.List[BaseAgent]):
        super().__init__(name, context)
        self.sub_agents = {agent.name: agent for agent in sub_agents}
        self.execution_order = [agent.name for agent in sub_agents] # Default sequential

    def run(self, input_data: typing.Any) -> typing.Any:
        self.log(f"Starting professional content workflow with input: {input_data}")
        # Persist the initial topic in the context for sub-agents to use as a source of truth
        if hasattr(self.context, 'topic'):
            self.context.topic = str(input_data).strip()
            
        current_data = input_data
        
        for agent_name in self.execution_order:
            agent = self.sub_agents[agent_name]
            self.log(f"Phase {self.execution_order.index(agent_name) + 1}: Delegating to {agent.name} ({agent.persona[:50]}...)")
            current_data = agent.run(current_data)
        
        self.log("Workflow orchestration complete. Content finalized.")
        return current_data
