from adk.agents import WorkflowAgent
from adk.core import AgentContext
from .trend_agent import TrendAgent
from .research_agent import ResearcherAgent
from .writer_agent import WriterAgent
from .seo_agent import SEOAgent
from .media_agent import MediaAgent
from .publisher_agent import PublisherAgent

class ManagerAgent(WorkflowAgent):
    def __init__(self, context: AgentContext):
        # Initialize sub-agents
        trend = TrendAgent(context)
        research = ResearcherAgent(context)
        writer = WriterAgent(context)
        seo = SEOAgent(context)
        media = MediaAgent(context)
        publisher = PublisherAgent(context)

        super().__init__(
            name="ManagerAgent", 
            context=context, 
            sub_agents=[trend, research, writer, seo, media, publisher]
        )
        self.persona = "You are an expert Content Manager. Your role is to orchestrate the content creation process, ensuring a smooth flow of tasks between specialized agents. You maintain the highest quality standards, overseeing the transition from initial trend identification to deep-dive research, professional writing, SEO optimization, media generation, and final publishing. You are the ultimate quality gatekeeper."
        
        # Define the strict sequential workflow
        self.execution_order = [
            "TrendAgent",
            "ResearcherAgent",
            "WriterAgent",
            "SEOAgent",
            "MediaAgent",
            "PublisherAgent"
        ]
