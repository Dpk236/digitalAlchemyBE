from Context.socket_context import socket_context
from Helpers.guardrail_manager import GuardrailManager
from Helpers.RedisKey import notes_key, summrize_key
from Helpers.ChatHistory.build_llm_messages_input import build_llm_messages
from Helpers.ChatHistory.add_chat_message import add_chat_message
from query_enum import Intent
from detect_intent import detect_intent
from handlers import (
    adaptive_rag_answer,
    fallback_rag_answer,
    handle_context_retrieval,
    handle_quiz_generation,
    handle_example_request,
    handle_timestamp_query,
    handle_fallback,
    handle_summarize_video,
    handle_quiz_explanation,
    handle_notes_creation,
)

guardrail_manager = GuardrailManager() # Default instance

def get_subject_from_id(video_id: str) -> str:
    """Guess subject from video_id or metadata."""
    if not video_id:
        return "physics"
    
    vid_lower = str(video_id).lower()
    if "bio" in vid_lower or "480989616" in vid_lower: # From file list observations
        return "biology"
    if "chem" in vid_lower:
        return "chemistry"
    if "physics" in vid_lower or "projectile" in vid_lower:
        return "physics"
        
    return "physics" # Default

def route_query(user_query: str, chat_history=[], summary: str = "", video_id=None, user_id=None, session_id=None):
    # Determine subject for guardrails
    subject = get_subject_from_id(video_id)
    
    # 🏁 GUARDRAIL CHECK 🏁
    # Initialize manager with specific subject
    manager = GuardrailManager(subject=subject)
    is_blocked, redirect_msg = manager.check_query(user_query)
    
    if is_blocked:
        print(f"🚫 Query blocked by guardrails ({subject}): {user_query}")
        return {
            "type": "guardrail_blocked",
            "response": redirect_msg,
            "query": user_query
        }

    intent_data = detect_intent(user_query, user_id=user_id, lecture_id=video_id, session_id=session_id)
    print("Detected intent:", intent_data.intent, type(intent_data))
    intent = intent_data.intent
    confidence = intent_data.confidence
    explanation_mode = intent_data.mode

    # 🔹 LOW CONFIDENCE → ASK CLARIFICATION
    if confidence < 0.65:
         return fallback_rag_answer(query =user_query, chat_history=chat_history, explanation_mode=explanation_mode, summary=summary, video_id=video_id)
        # return {
        #     "type": "clarification",
        #     "response": ("I want to help you correctly 😊<br/>"
        #                  "What do you want to do?<br/><br/>"),
        #     "data": {
        #         "cross_questions": ["1️⃣ Understand a lecture concept",
        #                             "2️⃣ Explain a quiz question",
        #                             "3️⃣ Explain something at a specific time in the video",
        #                             "4️⃣ Get a summary of the video"
        #                             ]
        #     }
        # }
    print("Detected Intent:", intent)
    if intent == Intent.CONTEXT_RETRIEVAL:
        return adaptive_rag_answer(user_query, chat_history=chat_history, explanation_mode=explanation_mode, summary=summary, video_id=video_id)

    if intent == Intent.QUIZ_GENERATION:
        return handle_quiz_generation(user_query, video_id=video_id, user_id=user_id, session_id=session_id)

    if intent == Intent.EXAMPLE_REQUEST:
        return handle_example_request(user_query)

    if intent == Intent.TIMESTAMP_QUERY:
        return handle_timestamp_query(user_query, chat_history=chat_history, summary=summary, video_id=video_id)

    if intent == Intent.SUMMARIZE_VIDEO:
        key = summrize_key(user_id, video_id, session_id)
        return handle_summarize_video(user_query, chat_history=chat_history, key=key)
    if intent == Intent.NOTES:
        key = notes_key(user_id, video_id, session_id)
        return handle_notes_creation(user_query, chat_history=chat_history, key=key)
    if intent == Intent.EXPLAIN_QUIZ_QUESTION:
        return handle_quiz_explanation(
            user_query, user_id, video_id, session_id, chat_history=chat_history,
            summary=summary
        )
    return handle_fallback(user_query)


if __name__ == "__main__":
    while True:
        try:
            user_query = input("User Query: ").strip()
            if not user_query:
                print("⚠️ Please enter a valid question.")
                continue

            print("User Query:", user_query)

            # 1️⃣ Store user message
            add_chat_message(user_id, lecture_id,
                             session_id, "user", user_query)

            # 2️⃣ Fetch chat history
            chat_history = build_llm_messages(user_id, lecture_id, session_id)

            # 3️⃣ Route query
            result = route_query(user_query, chat_history=chat_history)

            # 4️⃣ Handle fallback separately
            if result.get("type") == "fallback":
                print("AI Response:", result.get(
                    "message", "I didn’t understand that."))
                continue

            # 5️⃣ Success path
            ai_response = result.get("response")
            if not ai_response:
                raise ValueError("Empty AI response received")

            # 6️⃣ Store assistant message
            add_chat_message(
                user_id,
                lecture_id,
                session_id,
                "assistant",
                ai_response
            )

            print("AI Response:", ai_response)

        except KeyboardInterrupt:
            print("\n👋 Exiting chat...")
            break

        except Exception as e:
            # ❌ Do NOT store assistant message on error
            print("❌ Something went wrong while processing your question.")
            print("👉 Please try asking your question again.\n")

            # 🔍 Optional: log error for debugging
            print("DEBUG ERROR:", str(e))
