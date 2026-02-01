import requests
import os

def test_image_upload():
    url = "http://localhost:5000/ask-with-image"
    
    # Use an existing image from the directory for testing
    image_path = "/Users/deepak/Downloads/AskDoubt/Bryophyte.png"
    
    if not os.path.exists(image_path):
        print(f"Test image not found at {image_path}")
        return

    files = {'image': open(image_path, 'rb')}
    data = {
        'user_id': 'test_user_789',
        'video_id': 'Bio480989616',  # Using a valid video_id from the file list
        'session_id': 'test_session_abc'
    }

    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, files=files, data=data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("--- Success ---")
            print(f"Extracted Text: {result.get('extracted_text')}")
            print(f"AI Response: {result.get('ai_response')[:200]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Note: Make sure the server is running on port 5000 before running this script
    test_image_upload()
