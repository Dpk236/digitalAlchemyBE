from numpy import number
from Helpers.ChatHistory.fetch_last_messages import get_recent_messages
from Helpers.ChatHistory.retrieve_conversation_summary import get_summary


def build_llm_messages(
    user_id: str,
    lecture_id: str,
    session_id: str,
    limit: number = 6,
):
    messages = []

    summary = get_summary(user_id, lecture_id, session_id)
    print("summarysummary---", summary)
    if summary:
        messages.append({
            "role": "system",
            "content": f"Conversation summary so far:\n{summary}"
        })

    recent_messages = get_recent_messages(
        user_id, lecture_id, session_id, limit=limit
    )

    messages.extend(recent_messages)

    return messages
