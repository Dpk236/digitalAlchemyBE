import socketio
import eventlet
from flask import Flask

# from Helpers.ChatHistory.add_chat_message import add_chat_message
# from Helpers.ChatHistory.build_llm_messages_input import build_llm_messages
# from rewrite_followup import rewrite_query_if_needed
# from router import route_query

# -----------------------
# Socket.IO setup
# -----------------------
sio = socketio.Server(
    cors_allowed_origins="*",
    async_mode="eventlet"
)
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# -----------------------
# Socket lifecycle
# -----------------------
@sio.event
def connect(sid, environ):
    print(f"✅ Client connected: {sid}")

@sio.event
def disconnect(sid):
    print(f"❌ Client disconnected: {sid}")

# -----------------------
# Chat Event
# -----------------------
@sio.event
def chat_message(sid, data):
    """
    data = {
        user_id,
        lecture_id,
        session_id,
        message
    }
    """
    try:
        user_id = data["user_id"]
        lecture_id = data["lecture_id"]
        session_id = data["session_id"]
        user_query = data["message"]
        print(f"💬 Received message from {sid}: {user_query}")
        # # 1️⃣ Save user message
        # add_chat_message(user_id, lecture_id, session_id, "user", user_query)

        # # 2️⃣ Fetch chat history
        # chat_history = build_llm_messages(user_id, lecture_id, session_id)

        # # 3️⃣ Rewrite vague follow-ups
        # rewritten_query = rewrite_query_if_needed(user_query, chat_history)

        # # 4️⃣ Route query
        # result = route_query(rewritten_query, chat_history=chat_history)

        # if result.get("type") == "fallback":
        #     sio.emit(
        #         "chat_response",
        #         {"message": result.get("message", "I didn’t understand that.")},
        #         to=sid
        #     )
        #     return

        # ai_response = result["response"]

        # # 5️⃣ Save assistant response
        # add_chat_message(user_id, lecture_id, session_id, "assistant", ai_response)

        # 6️⃣ Send response
        sio.emit(
            "chat_response",
            {"message": "ai_response"},
            to=sid
        )

    except Exception as e:
        print("🔥 Socket error:", e)
        sio.emit(
            "chat_response",
            {
                "message": "Something went wrong. Please ask your question again."
            },
            to=sid
        )


# -----------------------
# Start server
# -----------------------
if __name__ == "__main__":
    print("🚀 Socket.IO server running on http://localhost:5000")
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)
