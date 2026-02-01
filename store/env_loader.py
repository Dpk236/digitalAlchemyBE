import os
from dotenv import load_dotenv
from pathlib import Path

def load_env():
    # Priority: ENV environment variable, else default to 'local'
    env = os.getenv("APP_ENV", "local")
    
    # Try loading .env.{env}
    env_file = f".env.{env}"
    env_path = Path(".") / env_file
    
    if env_path.exists():
        print(f"📡 Loading environment: {env} (from {env_file})")
        load_dotenv(env_path)
    else:
        # Fallback to standard .env if it exists
        if Path(".env").exists():
            print("📡 Loading default .env file")
            load_dotenv()
        else:
            print(f"⚠️ Warning: Neither {env_file} nor .env found.")

# Automatically load on import
load_env()
