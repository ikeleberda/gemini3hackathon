from adk.agents import LLMAgent
from adk.core import AgentContext
from tools.image_tool import ImageTool

class MediaAgent(LLMAgent):
    def __init__(self, context: AgentContext):
        super().__init__(
            name="MediaAgent", 
            context=context, 
            persona="""You are a Media Agent. Your responsibility is to generate high-quality visual assets that complement the content. You use Google Imagen 4 to create professional featured images and provide descriptive alt text for accessibility and SEO. Ensure the visual style aligns with the article's tone.""",
            tools=[ImageTool.generate_image]
        )

    def run(self, input_data: str) -> dict:
        self.log(f"Generating media for content...")
        
        # Parse content if SEO markers are present
        clean_content = input_data
        if "---ARTICLE---" in input_data:
            clean_content = input_data.split("---ARTICLE---")[-1].strip()
        
        # Simple prompt derivation: just ask for a relevant image
        prompt = f"Professional digital art for an article about: {clean_content[:150]}..."
        image_path = ImageTool.generate_image(prompt, api_key=self.context.google_api_key)
        
        # Generate Alt Text using LLM (delegated to super().run or handled here)
        alt_prompt = f"Generate a descriptive, SEO-friendly alt text for an image about: {clean_content[:200]}"
        alt_text = super().run(alt_prompt)
        
        self.log(f"Image generated at: {image_path}")
        self.log(f"Alt text generated: {alt_text}")
        
        return {
            "content": input_data,
            "image_path": image_path,
            "alt_text": alt_text
        }
