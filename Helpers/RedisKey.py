def chat_key(user_id: str, lecture_id: str, session_id: str) -> str:
    return f"chat:{user_id}:{lecture_id}:{session_id}"


def summary_key(user_id: str, lecture_id: str, session_id: str) -> str:
    return f"chat_summary:{user_id}:{lecture_id}:{session_id}"

def quiz_key(user_id: str, lecture_id: str, session_id: str) -> str:
    return f"quiz:{user_id}:{lecture_id}:{session_id}"

def summrize_key(user_id: str, lecture_id: str, session_id: str) -> str:
    return f"summarize:{user_id}:{lecture_id}:{session_id}"
def notes_key(user_id: str, lecture_id: str, session_id: str) -> str:
    return f"notes:{user_id}:{lecture_id}:{session_id}"
