import os
from google import genai
from google.genai import types
from PIL import Image
import io

class ImageTool:
    @staticmethod
    def generate_image(prompt: str, output_dir: str = "generated_assets", api_key: str = None) -> str:
        """
        Generate an image using Imagen 4 via Google GenAI SDK.
        Returns the local file path of the saved image.
        """
        use_vertex_for_images = os.environ.get("USE_VERTEX_FOR_IMAGES", "").lower() == "true"
        project = os.environ.get("GCP_PROJECT_ID")
        location = os.environ.get("GCP_LOCATION", "us-central1")

        if not api_key and not use_vertex_for_images:
            raise Exception("Missing Google API Key for image generation. Please set it in Settings.")

        try:
            print(f"  -> Tool Call: Generating image for '{prompt}'...")
            if use_vertex_for_images:
                print(f"  -> Using Vertex AI (Project: {project})")
                client = genai.Client(vertexai=True, project=project, location=location)
                model_id = 'publishers/google/models/imagen-4.0-generate-001'
            else:
                client = genai.Client(api_key=api_key)
                model_id = 'imagen-4.0-generate-001'
            
            # Using Imagen 4 model
            response = client.models.generate_images(
                model=model_id, 
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    aspect_ratio="16:9",
                    number_of_images=1
                )
            )

            if response.generated_images:
                image = response.generated_images[0]
                
                # Ensure output directory exists
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # Create a filename based on prompt or timestamp
                # Simple sanitization
                safe_prompt = "".join([c for c in prompt if c.isalnum() or c in (' ', '-', '_')]).strip()[:30]
                filename = f"{safe_prompt.replace(' ', '_')}.png"
                file_path = os.path.join(output_dir, filename)
                
                image.image.save(file_path)
                print(f"  -> SUCCESS: Image saved to {file_path}")
                return file_path
            else:
                print("  -> ERROR: No image generated.")
                return "error_no_image.png"

        except Exception as e:
            print(f"  -> ERROR: Image generation failed: {e}")
            # Fallback for demo continuity
            return "error_generating_image.png"
