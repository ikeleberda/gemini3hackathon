import yaml
import os
import sys

# Get variables from environment (already loaded by PowerShell)
# or pass them as arguments if needed.

env_vars = {
    "WP_URL": os.environ.get("WP_URL"),
    "WP_USERNAME": os.environ.get("WP_USERNAME"),
    "WP_APP_PASSWORD": os.environ.get("WP_APP_PASSWORD"),
    "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY"),
    "GOOGLE_MODEL_NAME": os.environ.get("GOOGLE_MODEL_NAME"),
    "GOOGLE_FALLBACK_MODELS": os.environ.get("GOOGLE_FALLBACK_MODELS"),
    "DATABASE_URL": sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DATABASE_URL"),
    "BACKEND_API_URL": sys.argv[2] if len(sys.argv) > 2 else os.environ.get("BACKEND_API_URL"),
    "NEXTAUTH_SECRET": sys.argv[3] if len(sys.argv) > 3 else os.environ.get("NEXTAUTH_SECRET"),
}

# Remove None values
env_vars = {k: v for k, v in env_vars.items() if v is not None}

with open("env.yaml", "w") as f:
    yaml.dump(env_vars, f, default_flow_style=False)

print("Generated env.yaml successfully")
