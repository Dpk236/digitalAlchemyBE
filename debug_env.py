import os
import store.env_loader

print("--- DEBUG ENV ---")
print(f"APP_ENV: {os.getenv('APP_ENV')}")
print(f"QDRANT_URL: {os.getenv('QDRANT_URL')}")
print(f"QDRANT_API_KEY: {os.getenv('QDRANT_API_KEY')}")
print("--- END DEBUG ---")
