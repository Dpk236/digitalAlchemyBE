import store.env_loader
from Context.socket_context import socket_context
from utility.extract_json_from_llm import save_quiz_locally
from LLMQueries.get_quiz import get_quiz
from Helpers.ChatHistory.get_chat_messages import get_chat_messages
from LLMQueries.get_flashcard import get_flashcard_query
from LLMQueries.get_visual_view import get_visual_view_query
from PyDantic.ResponseModel.response_model import ChatResponse
import socketio
import eventlet
from flask import Flask
from Helpers.ChatHistory.fetch_last_messages import get_recent_messages
from Helpers.ChatHistory.build_llm_messages_input import build_llm_messages
from route_query import route_query
from Helpers.ChatHistory.add_chat_message import add_chat_message
from flask_cors import CORS
from pathlib import Path
from flask import jsonify
import os
sio = socketio.Server(
    cors_allowed_origins="*",
    async_mode=os.getenv("ASYNC_MODE", "threading")
)
app = Flask(__name__)
CORS(app)
# app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app) # Not needed for threading mode usually or used differently
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
video_id = ""


@sio.event
def connect(sid, environ):
    query_string = environ.get('QUERY_STRING', '')
    print("Raw query:", query_string)
    # Parse manually
    from urllib.parse import parse_qs
    params = parse_qs(query_string)

    video_id = params.get('video_id', [None])[0]
    user_id = params.get('user_id', [None])[0]
    session_id = params.get('session_id', [None])[0]
    socket_context.set_video("video_id", video_id)
    socket_context.set_video("user_id", user_id)
    socket_context.set_video("session_id", session_id)
    print("video_id:", video_id, user_id, session_id)
    print(f"✅ Client connected: {sid}")


@sio.event
def disconnect(sid):
    socket_context.remove(sid)
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
        lecture_id = socket_context.get_video("video_id")
        session_id = data["session_id"]
        user_query = data["message"]
        print(f"💬 Received message from {sid}: {user_query}")
        # 1️⃣ Save user message
        add_chat_message(user_id, lecture_id, session_id, "user", user_query)

        # 2️⃣ Fetch chat history
        new_summary, recent_messages2 = get_chat_messages(
            user_id, lecture_id, session_id)
        print("chathistory ====", len(recent_messages2), recent_messages2)
        # return
        recent_messages = build_llm_messages(user_id, lecture_id, session_id)
        # return
        result = route_query(
            user_query, chat_history=recent_messages, summary=new_summary)
        print("result_type ===", result)
        result_type = result.get("type")
        ai_response = result["response"] if "response" in result else ""
        data = result.get("data", {})
        response = ChatResponse(
            type=result_type,
            ai_response=ai_response,
            data=data
        )
        res = response.json()
        if result_type == "fallback":
            sio.emit(
                "chat_response",
                res,
                to=sid
            )
            return
        if result_type == "clarification":
            sio.emit(
                "chat_response",
                res,
                to=sid
            )
            return
        # 5️⃣ Save assistant response
        add_chat_message(user_id, lecture_id, session_id,
                         "assistant", ai_response)

        sio.emit(
            "chat_response",
            res,
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


# handle cors preflight

@app.route("/get_summmary", methods=["GET"])
def get_summmary_of_video():
    video_id = socket_context.get_video("video_id")
    file_name = f"{video_id}_hierarchical_summary.json"
    print("file_name", file_name)
    if not Path(file_name).exists():
         return {"status": "401", "data": []}   
    with open(file_name,"r") as f:
        import json
        res = json.load(f)
        return res


@app.route("/visual-view", methods=["GET"])
def health_check():
    try:
        video_id = socket_context.get_video("video_id")
        with open(f"{video_id}_hierarchical_summary.json", "r") as f:
            import json
            res = json.load(f)
            final_summary = res["final_summary"]
            # data = get_visual_view_query(final_summary)
            # return {"status": "ok", "htmlContent": data}
            with open("simulator3.html", "r") as f:
                content = f.read()
                data = content if content else get_visual_view_query(final_summary)
                return {"status": "ok", "htmlContent": data}
    except ValueError as e:
        return {"status": "401", "data": [], "error": e}     


@app.route("/ai-flashcards", methods=["GET"])
def ai_flashcards():
    try:
        video_id = socket_context.get_video("video_id")
        summary_file = f"video_{video_id}_summaries.json"
        with open(summary_file, "r") as f:
            import json
            res = json.load(f)
            # The summaries file might be a list or the hierarchical dict
            final_summary = res["final_summary"] if isinstance(res, dict) and "final_summary" in res else str(res)
            
            flashcard_path = f"video_{video_id}_flashcards.json"
            if Path(flashcard_path).exists():
                with open(flashcard_path, "r") as f:
                    data = f.read().strip()
                return {"status": "ok", "data": json.loads(data)}
            else:
                data = get_flashcard_query(final_summary)
                # Save locally
                with open(flashcard_path, "w") as f:
                    f.write(data)
                return {"status": "ok", "data": json.loads(data)}
    except ValueError as e:
        return {"status": "401", "data": [], "error": e}
    
@app.route("/get-quiz", methods=["GET"])
def ai_quiz():
    try:
        video_id = socket_context.get_video("video_id")
        summary_file = f"video_{video_id}_summaries.json"
        with open(summary_file, "r") as f:
            import json
            res = json.load(f)
            final_summary = res["final_summary"] if isinstance(res, dict) and "final_summary" in res else str(res)
            quiz_path = f"video_{video_id}_quiz.json"
            if Path(quiz_path).exists():
                with open(quiz_path, "r") as f:
                    content = f.read().strip()
                    return {"status": "ok", "data": json.loads(content)}
            else:
                try:
                    print("final_summaryfinal_summary", len(final_summary))
                    data = get_quiz(final_summary)
                    print("datadatadata", data)
                    quiz = save_quiz_locally(data, quiz_path)
                    print("quizquiz", quiz)
                    return {"status": "ok", "data": quiz}
                except json.JSONDecodeError as e:
                    return jsonify({
                        "status": "401",
                        "error": "Invalid JSON returned by AI",
                        "message": str(e)
                    }), 500

                except Exception as e:
                    return jsonify({
                        "status": "401",
                        "error": "Internal server error",
                        "message": str(e)
                }), 500

    except ValueError as e:
        return {"status": "401", "data": [], "error": e}



@app.route("/get-all-chat", methods=["GET"])
def get_all_chats():
    try:
        user_id = socket_context.get_video("user_id")
        lecture_id = socket_context.get_video("video_id")
        session_id = socket_context.get_video("session_id")
        recent_messages = get_recent_messages(
            user_id, lecture_id, session_id, limit=6
        )
        return {"status": "ok", "data": recent_messages}
    except ValueError as e:
        return {"status": "401", "data": [], "error": e}


# -----------------------
# Start server
# -----------------------
if __name__ == "__main__":
    print("🚀 Socket.IO server running on http://localhost:5000")
    # Using standard flask for threading mode
    app.run(host="0.0.0.0", port=5000, debug=True)
