import os
import re
import typing
from adk.agents import LLMAgent
from adk.core import AgentContext
from tools.wordpress_tool import WordPressTool

class PublisherAgent(LLMAgent):
    def __init__(self, context: AgentContext):
        super().__init__(
            name="PublisherAgent", 
            context=context, 
            persona="""You are a Professional Publisher Agent. Your role is to format the final content and push it to the WordPress API. You handle multiple site credentials, ensure correct HTML formatting (converting from Markdown), upload featured images, and include all SEO metadata (meta tags, JSON-LD, slugs) in the final post.""",
            tools=[WordPressTool.publish_post]
        )

    def run(self, input_data: typing.Union[str, dict]) -> str:
        self.log("Formatting and publishing content to WordPress...")
        
        # Check for simulation safeguard
        is_simulated = getattr(self.context, 'is_simulated', False)
        
        content = ""
        image_path = None
        
        if isinstance(input_data, dict):
            content = input_data.get("content", "")
            image_path = input_data.get("image_path")
        else:
            content = input_data

        # Parse SEO Meta Data if present
        seo_meta = {}
        
        if "---SEO_DATA---" in content:
            parts = content.split("---ARTICLE---")
            
            # Parse the metadata section
            seo_part = parts[0].replace("---SEO_DATA---", "").strip()
            for line in seo_part.split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    seo_meta[k.strip().lower()] = v.strip()
            
            # Update content to be just the article part
            if len(parts) > 1:
                content = parts[1].strip()

        # Remove the reference links section (cleanup)
        if "---VALIDATED_LINKS_FOR_REFERENCE_ONLY---" in content:
            content = content.split("---VALIDATED_LINKS_FOR_REFERENCE_ONLY---")[0].strip()

        # Retrieve credentials
        wp_sites = []
        wp_urls = os.environ.get("WP_URLS", os.environ.get("WP_URL", ""))
        wp_users = os.environ.get("WP_USERNAMES", os.environ.get("WP_USERNAME", ""))
        wp_passes = os.environ.get("WP_APP_PASSWORDS", os.environ.get("WP_APP_PASSWORD", ""))
        
        if wp_urls and wp_users and wp_passes:
            urls = [u.strip() for u in wp_urls.split(",")]
            users = [u.strip() for u in wp_users.split(",")]
            passes = [p.strip() for p in wp_passes.split(",")]
            for u, usr, p in zip(urls, users, passes):
                wp_sites.append({"url": u, "username": usr, "password": p})
        
        if not wp_sites:
            return "FAILED: No WordPress credentials provided."

        # Convert Markdown to HTML
        try:
            import markdown
            html_content = markdown.markdown(content, extensions=['extra', 'nl2br'])
        except:
            html_content = content

        # Determine publishing status
        publish_status = "publish"
        notice = ""
        if is_simulated:
            publish_status = "draft"
            notice = '<div style="background:#fff9c4;padding:15px;border:1px solid #fbc02d;margin-bottom:20px;"><strong>⚠️ NOTICE:</strong> This content was generated in <em>Simulation Mode</em> because the primary AI model hit a quota limit or error. It has been saved as a <strong>DRAFT</strong> for your review.</div>'
            html_content = notice + html_content

        results = []
        for auth_data in wp_sites:
            site_url = auth_data.get("url")
            
            # Upload image if provided
            featured_media_id = None
            if image_path:
                media_result = WordPressTool.upload_media(image_path, auth_data)
                if media_result: featured_media_id = media_result.get("id")

            # Extract title
            title = seo_meta.get("meta title") or (f"Mastering {self.context.topic}" if hasattr(self.context, 'topic') else "Agentic AI Report")
            
            # Resolve Categories
            cat_ids = []
            cat_names = seo_meta.get("category", "").split(",")
            for cat in cat_names:
                cat = cat.strip()
                if cat:
                    cat_id = WordPressTool.get_or_create_term(cat, "categories", auth_data)
                    if cat_id:
                        cat_ids.append(cat_id)

            # Resolve Tags
            tag_ids = []
            tag_names = seo_meta.get("tags", "").split(",")
            for tag in tag_names:
                tag = tag.strip()
                if tag:
                    tag_id = WordPressTool.get_or_create_term(tag, "tags", auth_data)
                    if tag_id:
                        tag_ids.append(tag_id)

            # Publish to WordPress
            try:
                result_url = WordPressTool.publish_post(
                    title, 
                    html_content, 
                    auth=auth_data, 
                    featured_media_id=featured_media_id,
                    status=publish_status, # Use dynamic status
                    slug=seo_meta.get("slug"),
                    excerpt=seo_meta.get("meta description"),
                    categories=cat_ids,
                    tags=tag_ids
                )
                
                # Check for failure string from tool (tool returns "FAILED: ..." string on error)
                if result_url and str(result_url).startswith("FAILED"):
                    raise Exception(result_url)

                status_label = "Published" if publish_status == "publish" else "Saved as Draft"
                res_msg = f"**{status_label} ({site_url}):** [View Post]({result_url})"
                results.append(res_msg)
                
            except Exception as e:
                # Retry as draft if the first attempt failed and we weren't already trying draft
                # This handles cases where 'publish' fails but 'draft' might work (permissions, etc)
                if publish_status == "publish":
                    try:
                        print(f"  -> Publishing failed ({e}), retrying as draft...")
                        result_url = WordPressTool.publish_post(
                            title, 
                            html_content, 
                            auth=auth_data, 
                            featured_media_id=featured_media_id,
                            status="draft", 
                            slug=seo_meta.get("slug"),
                            excerpt=seo_meta.get("meta description"),
                            categories=cat_ids,
                            tags=tag_ids
                        )
                        
                        if result_url and str(result_url).startswith("FAILED"):
                             raise Exception(result_url)

                        res_msg = f"**Saved as Draft (Fallback) ({site_url}):** [View Post]({result_url})"
                        results.append(res_msg)
                        continue # Skip the failure append below
                    except Exception as retry_e:
                        e = retry_e # Update e to show the draft failure reason

                results.append(f"**Failed ({site_url}):** {str(e)}")
            
        return "### Content Processing Complete\n\n" + "\n\n".join(results)
