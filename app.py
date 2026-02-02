"""
Flask HTTP wrapper for Cloud Run deployment.
Provides HTTP endpoints to trigger the multi-agent content system.
"""
import os
import sys
import json
import re
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from adk.core import AgentContext
from agents.manager_agent import ManagerAgent

app = Flask(__name__)

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run"""
    return jsonify({
        'status': 'healthy',
        'service': 'fractal-aphelion-backend',
        'version': '1.0.0'
    }), 200

@app.route('/run', methods=['POST'])
def run_agents():
    """
    Trigger the multi-agent content system.
    
    Request body:
    {
        "topic": "Your topic here",
        "wp_config": {
            "url": "...",
            "username": "...",
            "password": "..."
        }
    }
    """
    try:
        # Get topic from request
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({
                'error': 'Missing required field: topic',
                'example': {'topic': 'Agentic AI'}
            }), 400
        
        topic = data['topic']
        wp_config = data.get('wp_config', {})
        db_url = data.get('db_url')
        job_id = data.get('job_id')
        google_api_key = data.get('google_api_key')
        google_model_name = data.get('google_model_name')
        google_fallback_models = data.get('google_fallback_models')
        
        # Override environment variables for the current request context
        if wp_config:
            if wp_config.get('url'): os.environ['WP_URL'] = wp_config['url']
            if wp_config.get('username'): os.environ['WP_USERNAME'] = wp_config['username']
            if wp_config.get('password'): os.environ['WP_APP_PASSWORD'] = wp_config['password']
        
        print(f"Starting workflow with topic: '{topic}' [Job: {job_id}]")
        
        # Create shared context
        context = AgentContext()
        context.topic = topic
        context.db_url = db_url
        context.job_id = job_id
        # Use provided value or fallback to environment variables
        context.google_api_key = google_api_key or os.environ.get('GOOGLE_API_KEY')
        context.google_model_name = google_model_name or os.environ.get('GOOGLE_MODEL_NAME')
        context.google_fallback_models = google_fallback_models or os.environ.get('GOOGLE_FALLBACK_MODELS')
        
        # Initialize the Manager
        manager = ManagerAgent(context)
        
        # Run the workflow
        try:
            result = manager.run(topic)
            print(f"Workflow completed successfully")

            # Final DB update for completion
            if db_url and job_id:
                try:
                    logs = "\n".join(context.history)
                    combined_output = logs + "\n" + str(result)
                    
                    url_match = re.search(r"\[View Post\]\((https?://[^\s)]+)\)", combined_output)
                    published_url = url_match.group(1) if url_match else None
                    if not published_url:
                        fallback_match = re.search(r"SUCCESS: Post published at\s*(https?://[^\s]+)", combined_output)
                        if fallback_match: published_url = fallback_match.group(1)
                    
                    title_match = re.search(r"Final Title: (.*)", logs)
                    published_title = title_match.group(1).strip() if title_match else None

                    is_simulated = getattr(context, 'is_simulated', False)
                    is_draft = "Saved as Draft" in str(result) or "retrying as draft" in combined_output
                    
                    if published_url:
                        final_status = "DRAFT" if (is_simulated or is_draft) else "PUBLISHED"
                        if is_simulated: logs += "\n[System] Post saved as DRAFT due to Simulated Mode."
                        elif is_draft: logs += "\n[System] Post saved as DRAFT due to Publishing Fallback."
                    else:
                        final_status = "FAILED"
                        logs += "\n[System] Publishing failed: " + ("Skipped due to simulation" if is_simulated else "No WordPress URL found.")

                    if db_url.startswith("file:") or "sqlite" in db_url.lower():
                        import sqlite3
                        db_path = db_url.replace("file:", "")
                        if "?" in db_path: db_path = db_path.split("?")[0]
                        conn = sqlite3.connect(db_path)
                        cur = conn.cursor()
                        cur.execute('UPDATE "AgentJob" SET "status" = ?, "logs" = ?, "currentStep" = ?, "updatedAt" = CURRENT_TIMESTAMP WHERE "id" = ?', ("COMPLETED", logs, "Completed", job_id))
                        cur.execute('SELECT "contentItemId" FROM "AgentJob" WHERE "id" = ?', (job_id,))
                        cid = cur.fetchone()[0]
                        cur.execute('UPDATE "ContentItem" SET "status" = ?, "publishedUrl" = ?, "title" = COALESCE(?, "title"), "updatedAt" = CURRENT_TIMESTAMP WHERE "id" = ?', (final_status, published_url, published_title, cid))
                    else:
                        import psycopg2
                        clean_url = db_url.split("?")[0] if "?" in db_url else db_url
                        conn = psycopg2.connect(clean_url)
                        cur = conn.cursor()
                        cur.execute('UPDATE "AgentJob" SET "status" = %s, "logs" = %s, "currentStep" = %s, "updatedAt" = NOW() WHERE "id" = %s', ("COMPLETED", logs, "Completed", job_id))
                        cur.execute('SELECT "contentItemId" FROM "AgentJob" WHERE "id" = %s', (job_id,))
                        cid = cur.fetchone()[0]
                        cur.execute('UPDATE "ContentItem" SET "status" = %s, "publishedUrl" = %s, "title" = COALESCE(%s, "title"), "updatedAt" = NOW() WHERE "id" = %s', (final_status, published_url, published_title, cid))

                    conn.commit()
                    cur.close()
                    conn.close()
                except Exception as final_db_err:
                    print(f"[FINAL DB ERROR] {final_db_err}")

            return jsonify({
                'status': 'success',
                'topic': topic,
                'result': result,
                'logs': context.history
            }), 200
        except Exception as e:
            # Update AgentJob with failure
            if db_url and job_id:
                try:
                    logs = "\n".join(context.history) + f"\nERROR: {str(e)}"
                    if db_url.startswith("file:") or "sqlite" in db_url.lower():
                        import sqlite3
                        db_path = db_url.replace("file:", "")
                        if "?" in db_path: db_path = db_path.split("?")[0]
                        conn = sqlite3.connect(db_path)
                        cur = conn.cursor()
                        cur.execute('UPDATE "AgentJob" SET "status" = ?, "logs" = ?, "updatedAt" = CURRENT_TIMESTAMP WHERE "id" = ?', ("FAILED", logs, job_id))
                    else:
                        import psycopg2
                        clean_url = db_url.split("?")[0] if "?" in db_url else db_url
                        conn = psycopg2.connect(clean_url)
                        cur = conn.cursor()
                        cur.execute('UPDATE "AgentJob" SET "status" = %s, "logs" = %s, "updatedAt" = NOW() WHERE "id" = %s', ("FAILED", logs, job_id))
                    conn.commit()
                    cur.close()
                    conn.close()
                except: pass
            raise e
        
    except Exception as e:
        print(f"Error running workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify configuration"""
    return jsonify({
        'status': 'ok',
        'environment': {
            'wp_url': os.environ.get('WP_URL', 'not set'),
            'wp_username': os.environ.get('WP_USERNAME', 'not set'),
            'google_api_key_present': bool(os.environ.get('GOOGLE_API_KEY')),
            'google_search_api_key_present': bool(os.environ.get('GOOGLE_SEARCH_API_KEY')),
            'gcp_project_id': os.environ.get('GCP_PROJECT_ID', 'not set'),
            'use_vertex_ai': os.environ.get('USE_VERTEX_AI', 'not set'),
            'use_vertex_for_images': os.environ.get('USE_VERTEX_FOR_IMAGES', 'not set')
        }
    }), 200

if __name__ == '__main__':
    # For local testing
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
