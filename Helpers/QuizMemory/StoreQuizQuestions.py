from typing import Any
from Helpers.RedisKey import quiz_key
from store import redis_connection
import json
redis_client = redis_connection.return_redis_client()
QUIZ_TTL_SECONDS = 30 * 60 # 30 minutes
def store_quiz_questions(
    user_id: str,
    lecture_id: str,
    session_id: str,
    quiz_questions: Any
):
    """
    quiz_questions = [
        {
            "question_id": "Q4",
            "question_text": "...",
            "options": {...},
            "correct_answer": "C",
            "correct_answer_text": "...",
            "explanation": "...",
            "timestamps": ["00:00:44"]
        }
    ]
    """

    key = quiz_key(user_id, lecture_id, session_id)
    print("Storing Quiz Questions at key:", key, len(quiz_questions))
    for q in quiz_questions:
        print("Storing Quiz Question:", q["question_id"], q["question_text"])
        redis_client.hset(
            key,
            q["question_id"],
            json.dumps(q)
        )

    redis_client.expire(key, QUIZ_TTL_SECONDS)
