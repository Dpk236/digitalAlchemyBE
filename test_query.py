import os
import json
from route_query import route_query
from Context.socket_context import socket_context

def test_query(prompt: str, video_id: str, user_id: str, session_id: str):
    print(f"\n❓ Query: {prompt}")
    print("-" * 30)
    
    # Simulate the query routing
    result = route_query(
        prompt, 
        chat_history=[], 
        video_id=video_id, 
        user_id=user_id, 
        session_id=session_id
    )
    
    print("\n✅ Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    video_id = "waves"
    user_id = "user_test_123"
    session_id = "session_test_456"

    # We also set it in context just in case some sub-functions still use it (though they shouldn't with the args passed)
    MOCK_SID = "test_sid"
    socket_context.set_context(MOCK_SID, "video_id", video_id)
    socket_context.set_context(MOCK_SID, "user_id", user_id)
    socket_context.set_context(MOCK_SID, "session_id", session_id)

    print("\n--- Testing Dynamic Summarization ---")
    test_query("Summarize this video for me.", video_id, user_id, session_id)
    
    print("\n--- Testing Dynamic Quiz Generation ---")
    test_query("Can you generate a quiz based on this lecture?", video_id, user_id, session_id)
    
    print("\n--- Testing Dynamic Flashcard Generation ---")
    from LLMQueries.get_flashcard import get_flashcard_query
    # We need a summary first
    summary_path = f"video_{video_id}_summaries.json"
    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            res = json.load(f)
            summary = str(res)
            flashcards = get_flashcard_query(summary)
            print("\n✅ Flashcards Generated:")
            print(flashcards[:500] + "...")
    else:
        print(f"⚠️ {summary_path} not found. Skip flashcard test.")
