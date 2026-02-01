from Context.socket_context import socket_context
from Helpers.RedisKey import chat_key
from store.redis_connection import return_redis_client
import json
CHAT_TTL_SECONDS = 30 * 60  # 30 minutes
redis_client = return_redis_client()
def add_chat_message(
    user_id: str,
    lecture_id: str,
    session_id: str,
    role: str,
    content: str
):
    key = chat_key(user_id, lecture_id, session_id)
    message = json.dumps({
        "role": role,
        "content": content
    })

    redis_client.rpush(key, message)
    redis_client.expire(key, CHAT_TTL_SECONDS)
