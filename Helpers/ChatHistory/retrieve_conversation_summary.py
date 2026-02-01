from Helpers.RedisKey import summary_key
from store.redis_connection import return_redis_client
redis_client = return_redis_client()
def get_summary(
    user_id: str,
    lecture_id: str,
    session_id: str
) -> str | None:
    key = summary_key(user_id, lecture_id, session_id)
    return redis_client.get(key)
