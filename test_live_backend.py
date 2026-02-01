import requests
import socketio
import time
import json

BASE_URL = "https://askdoubt-backend.onrender.com"
VIDEO_ID = "waves"
USER_ID = "user_live_test"
SESSION_ID = "session_live_test"

def test_http_endpoints():
    print("\n--- Testing HTTP GET Endpoints ---")
    
    # 1. Test Quiz Endpoint
    print(f"📡 Requesting Quiz for video: {VIDEO_ID}...")
    try:
        response = requests.get(f"{BASE_URL}/get-quiz?video_id={VIDEO_ID}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Quiz Data Received (snippet):")
            print(json.dumps(data, indent=2)[:500] + "...")
    except Exception as e:
        print(f"❌ Quiz Error: {e}")

    # 2. Test Flashcards Endpoint
    print(f"\n📡 Requesting Flashcards for video: {VIDEO_ID}...")
    try:
        response = requests.get(f"{BASE_URL}/ai-flashcards?video_id={VIDEO_ID}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Flashcard Data Received (snippet):")
            print(json.dumps(data, indent=2)[:500] + "...")
    except Exception as e:
        print(f"❌ Flashcard Error: {e}")

def test_socket_chat():
    print("\n--- Testing Socket.IO Chat (Summarization) ---")
    sio = socketio.Client()

    @sio.event
    def connect():
        print("✅ Connected to Socket.IO server!")
        # Send a message to summarize
        message_data = {
            "user_id": USER_ID,
            "session_id": SESSION_ID,
            "message": "Summarize this video for me."
        }
        print(f"📤 Sending: {message_data['message']}")
        sio.emit('chat_message', message_data)

    @sio.on('chat_response')
    def on_message(data):
        print("\n📥 Received Response from AI:")
        print("-" * 30)
        try:
            # Parse if it's a string, otherwise use directly
            parsed_data = json.loads(data) if isinstance(data, str) else data
            print(parsed_data.get('ai_response', 'No response content'))
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Raw data: {data}")
        print("-" * 30)
        sio.disconnect()

    try:
        # Add query params for connection context
        connection_url = f"{BASE_URL}?video_id={VIDEO_ID}&user_id={USER_ID}&session_id={SESSION_ID}"
        sio.connect(connection_url, wait_timeout=20)
        sio.wait()
    except Exception as e:
        print(f"❌ Socket.IO Error: {e}")

if __name__ == "__main__":
    test_http_endpoints()
    test_socket_chat()
