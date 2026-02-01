from Helpers.RedisKey import quiz_key
from store import redis_connection
import json

redis_client = redis_connection.return_redis_client()
def get_quiz_question(
    user_id: str,
    lecture_id: str,
    session_id: str,
    question_id: str
) -> dict | None:

    key = quiz_key(user_id, lecture_id, session_id)

    data = redis_client.hget(key, question_id)
    if not data:
        return None

    return json.loads(data)
def get_all_quiz_questions(
    user_id: str,
    lecture_id: str,
    session_id: str
) -> list[dict]:

    key = quiz_key(user_id, lecture_id, session_id)
    raw = redis_client.hgetall(key)

    return [json.loads(v) for v in raw.values()]



