import redis
from typing import List, Dict

import os

# Use REDIS_URL for Render, fallback to localhost for development
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.from_url(
    redis_url,
    decode_responses=True  # important (strings, not bytes)
)

def return_redis_client() -> redis.Redis:
    return redis_client