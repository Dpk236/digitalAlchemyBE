import eventlet
eventlet.monkey_patch()

import store.env_loader
from Context.socket_context import socket_context
from utility.extract_json_from_llm import save_quiz_locally
from LLMQueries.get_quiz import get_quiz
from Helpers.ChatHistory.get_chat_messages import get_chat_messages
from LLMQueries.get_flashcard import get_flashcard_query
from LLMQueries.get_visual_view import get_visual_view_query
from PyDantic.ResponseModel.response_model import ChatResponse
import socketio
from flask import Flask, request
from Helpers.ChatHistory.fetch_last_messages import get_recent_messages
from Helpers.ChatHistory.build_llm_messages_input import build_llm_messages
from route_query import route_query
from Helpers.ChatHistory.add_chat_message import add_chat_message
from flask_cors import CORS
from pathlib import Path
from flask import jsonify
import os
import json
from Services.SummarizeChunks.summarize_chunks import SummarizeChunks
from Services.OCR.ocr_service import OCRService
import base64

# Use eventlet as default for Render compatibility
sio = socketio.Server(
    cors_allowed_origins="*",
    async_mode=os.getenv("ASYNC_MODE", "eventlet")
)
app = Flask(__name__)
CORS(app)

@app.route("/")
def health_check():
    return jsonify({
        "status": "live",
        "service": "AskDoubt Backend",
        "message": "API is running successfully on Render!"
    })

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
    socket_context.set_context(sid, "video_id", video_id)
    socket_context.set_context(sid, "user_id", user_id)
    socket_context.set_context(sid, "session_id", session_id)
    print("video_id:", video_id, user_id, session_id)
    print("Client connected: {}".format(sid))


@sio.event
def disconnect(sid):
    socket_context.remove(sid)
    print("Client disconnected: {}".format(sid))

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
        lecture_id = socket_context.get_context(sid, "video_id")
        session_id = data["session_id"]
        user_query = data["message"]
        print("Received message from {}: {}".format(sid, user_query))
        # 1 Save user message
        add_chat_message(user_id, lecture_id, session_id, "user", user_query)

        # 2 Fetch chat history
        new_summary, recent_messages2 = get_chat_messages(
            user_id, lecture_id, session_id)
        print("chathistory ====", len(recent_messages2), recent_messages2)
        # return
        recent_messages = build_llm_messages(user_id, lecture_id, session_id)
        # return
        result = route_query(
            user_query, chat_history=recent_messages, summary=new_summary, 
            video_id=lecture_id, user_id=user_id, session_id=session_id)
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
        # 5 Save assistant response
        add_chat_message(user_id, lecture_id, session_id,
                         "assistant", ai_response)

        sio.emit(
            "chat_response",
            res,
            to=sid
        )

    except Exception as e:
        print("Socket error:", e)
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
    video_id = request.args.get("video_id")
    if not video_id:
        return {"status": "400", "data": "Missing video_id"}
    file_name = "{}_hierarchical_summary.json".format(video_id)
    print("file_name", file_name)
    if not Path(file_name).exists():
         return {"status": "401", "data": []}   
    with open(file_name,"r") as f:
        import json
        res = json.load(f)
        return res


@app.route("/visual-view", methods=["GET"])
def visual_view():
    try:
        video_id = request.args.get("video_id")
        if not video_id:
            return "Missing video_id"
        with open("{}_hierarchical_summary.json".format(video_id), "r") as f:
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


def get_summary_content(video_id):
    """Robustly retrieves summary content, generating if missing."""
    summary_patterns = [
        "video_{}_summaries.json".format(video_id),
        "{}_hierarchical_summary.json".format(video_id),
        "{}_chunk_summaries.json".format(video_id)
    ]
    
    for pattern in summary_patterns:
        if Path(pattern).exists():
            with open(pattern, "r") as f:
                res = json.load(f)
                # Handle hierarchical format
                if isinstance(res, dict) and "final_summary" in res:
                    return res["final_summary"]
                # Handle list format
                elif isinstance(res, list):
                    return "\n".join([item.get("summary", "") for item in res])
                # Handle plain string
                return str(res)
                
    # If not found, generate it
    print("🚀 Summary not found to trigger generation for {}".format(video_id))
    SummarizeChunks(video_id)
    
    # Check again (at least for the pattern generated by SummarizeChunks)
    for pattern in summary_patterns:
        if Path(pattern).exists():
            with open(pattern, "r") as f:
                res = json.load(f)
                if isinstance(res, dict) and "final_summary" in res:
                    return res["final_summary"]
    return None


@app.route("/ai-flashcards", methods=["GET"])
def ai_flashcards():
    try:
        video_id = request.args.get("video_id")
        if not video_id:
            return {"status": "400", "error": "Missing video_id"}
        final_summary = get_summary_content(video_id)
        if not final_summary:
            return {"status": "400", "error": "Could not retrieve or generate summary for video_id: {}".format(video_id)}
            
        flashcard_path = "video_{}_flashcards.json".format(video_id)
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
        video_id = request.args.get("video_id")
        if not video_id:
            return {"status": "400", "error": "Missing video_id"}
        final_summary = get_summary_content(video_id)
        if not final_summary:
            return {"status": "400", "error": "Could not retrieve or generate summary for video_id: {}".format(video_id)}
        
        quiz_path = "video_{}_quiz.json".format(video_id)
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
        user_id = request.args.get("user_id")
        lecture_id = request.args.get("video_id")
        session_id = request.args.get("session_id")
        recent_messages = get_recent_messages(
            user_id, lecture_id, session_id, limit=6
        )
        return {"status": "ok", "data": recent_messages}
    except ValueError as e:
        return {"status": "401", "data": [], "error": e}


# -----------------------
# Image Upload Route
# -----------------------

ocr_service = OCRService()

@app.route("/ask-with-image", methods=["POST"])
def ask_with_image():
    try:
        if 'image' not in request.files:
            return jsonify({"status": "400", "error": "No image part"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"status": "400", "error": "No selected file"}), 400

        user_id = request.form.get("user_id")
        video_id = request.form.get("video_id")
        session_id = request.form.get("session_id")

        if not all([user_id, video_id, session_id]):
            return jsonify({"status": "400", "error": "Missing user_id, video_id, or session_id"}), 400

        # Read and encode image
        image_bytes = file.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # 1. Extract text from image
        print(f"📷 Extracting text from image for user {user_id}...")
        extracted_text = ocr_service.extract_text_from_image(base64_image)
        print(f"📝 Extracted text: {extracted_text}")

        if not extracted_text:
            return jsonify({"status": "400", "error": "Could not extract text from image"}), 400

        # 2. Save user message (extracted text)
        add_chat_message(user_id, video_id, session_id, "user", f"[Image Upload] {extracted_text}")

        # 3. Fetch chat history and summary
        summary, _ = get_chat_messages(user_id, video_id, session_id)
        chat_history = build_llm_messages(user_id, video_id, session_id)

        # 4. Route query through RAG
        result = route_query(
            extracted_text, 
            chat_history=chat_history, 
            summary=summary, 
            video_id=video_id, 
            user_id=user_id, 
            session_id=session_id
        )

        ai_response = result.get("response", "")
        result_type = result.get("type", "context_retrieval")

        # 5. Save assistant response
        add_chat_message(user_id, video_id, session_id, "assistant", ai_response)

        return jsonify({
            "status": "ok",
            "extracted_text": extracted_text,
            "ai_response": ai_response,
            "type": result_type,
            "data": result.get("data", {})
        })

    except Exception as e:
        print(f"❌ Error in /ask-with-image: {str(e)}")
        return jsonify({"status": "500", "error": str(e)}), 500

# -----------------------
# Start server
# -----------------------
if __name__ == "__main__":
    print("Socket.IO server running on http://localhost:5000")
    from gevent.pywsgi import WSGIServer
    from geventwebsocket.handler import WebSocketHandler

    http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
