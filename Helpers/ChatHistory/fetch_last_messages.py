from typing import List, Dict
import json
from Helpers.RedisKey import chat_key
from store.redis_connection import return_redis_client
redis_client = return_redis_client()
def get_recent_messages(
    user_id: str,
    lecture_id: str,
    session_id: str,
    limit: int = 6
) -> List[Dict]:
    key = chat_key(user_id, lecture_id, session_id)

    messages = redis_client.lrange(key, -limit, -1)
    return [json.loads(m) for m in messages]
