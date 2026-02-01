from Helpers.RedisKey import summary_key
from store.redis_connection import return_redis_client
redis_client = return_redis_client()
CHAT_TTL_SECONDS = 30 * 60  # 30 minutes
def save_summary(
    user_id: str,
    lecture_id: str,
    session_id: str,
    summary_text: str
):
    key = summary_key(user_id, lecture_id, session_id)

    redis_client.set(key, summary_text)
    redis_client.expire(key, CHAT_TTL_SECONDS)
