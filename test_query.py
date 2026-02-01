import os
import json
from route_query import route_query
from Context.socket_context import socket_context

# Mock the socket context for testing
socket_context.set_video("video_id", "projectile_motion")

def test_query(prompt: str):
    print(f"\n❓ Query: {prompt}")
    print("-" * 30)
    
    # Simulate the query routing
    result = route_query(prompt, chat_history=[])
    
    print("\n✅ Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    # Set context for Waves
    socket_context.set_video("video_id", "waves")
    socket_context.set_video("user_id", "user_test_123")
    socket_context.set_video("session_id", "session_test_456")

    print("\n--- Testing Dynamic Summarization ---")
    test_query("Summarize this video for me.")
    
    print("\n--- Testing Dynamic Quiz Generation ---")
    test_query("Can you generate a quiz based on this lecture?")
    
    print("\n--- Testing Dynamic Flashcard Generation ---")
    # Simulate the /ai-flashcards endpoint logic
    from LLMQueries.get_flashcard import get_flashcard_query
    # We need a summary first
    with open(f"video_waves_summaries.json", "r") as f:
        res = json.load(f)
        summary = str(res)
        flashcards = get_flashcard_query(summary)
        print("\n✅ Flashcards Generated:")
        print(flashcards[:500] + "...")
