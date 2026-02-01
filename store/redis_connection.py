import redis
from typing import List, Dict

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True  # important (strings, not bytes)
)
def return_redis_client() -> redis.Redis:
    return redis_client