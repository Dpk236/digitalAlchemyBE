from Helpers.ChatHistory.fetch_last_messages import get_recent_messages
from LLMQueries.get_summary_chat import summarize_messages
from store.redis_connection import return_redis_client
import json

MAX_MESSAGES = 5
redis_client = return_redis_client()
def get_chat_messages(user_id, lecture_id, session_id):
    key = f"chat:{user_id}:{lecture_id}:{session_id}:messages"
    summary_key = f"chat:{user_id}:{lecture_id}:{session_id}:summary"
    messages = get_recent_messages(
        user_id, lecture_id, session_id, limit=100
    )
    if len(messages) <= MAX_MESSAGES:
        summary = redis_client.get(summary_key)
        return summary, messages

    # Split old + recent
    old_messages = messages[:-MAX_MESSAGES]
    recent_messages = messages[-MAX_MESSAGES:]
    print("messafeweee recent_messages", len(old_messages), recent_messages )


    # Update summary
    existing_summary = redis_client.get(summary_key) or ""
    print("new existing_summary", existing_summary)

    new_summary = summarize_messages(existing_summary, old_messages)
    print("new new_summarynew_summarynew_summary", new_summary)

    redis_client.set(summary_key, new_summary)

    # Trim Redis list to last 5
    redis_client.ltrim(key, -MAX_MESSAGES, -1)

    return new_summary, recent_messages
