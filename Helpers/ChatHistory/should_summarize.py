from Helpers.RedisKey import chat_key
from store.redis_connection import return_redis_client
redis_client = return_redis_client()

def should_summarize(
    user_id: str,
    lecture_id: str,
    session_id: str,
    threshold: int = 8
) -> bool:
    key = chat_key(user_id, lecture_id, session_id)
    count = redis_client.llen(key)
    return count >= threshold
