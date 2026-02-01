import requests
import json
import base64
import os
from dotenv import load_dotenv

load_dotenv()

# Azure Configuration
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT") + "openai/deployments/" + os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") + "/chat/completions?api-version=" + os.getenv("AZURE_OPENAI_API_VERSION")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
HEADERS = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}
USER_IMAGE_FOLDER = "./image_question"

def encode_image(image_path):
    """Encodes an image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_user_images():
    """Returns a list of image filenames in the user image folder."""
    if not os.path.exists(USER_IMAGE_FOLDER):
        return []
    return [f for f in os.listdir(USER_IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

import sys
from Services.Embedding.sentence_transform_embeddings import SentenceTransformerEmbeddings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def chat_with_docs():
    COLLECTION_NAME = "hackathon_docs"
    
    # Load the model and connect to existing DB
    embeddings_model = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")
    vectorstore = QdrantVectorStore.from_existing_collection(
        embedding=embeddings_model,
        collection_name=COLLECTION_NAME,
        url="http://localhost:6333"
    )

    print("\n--- Multimodal PDF Search & QA (Azure OpenAI GPT-4) ---")
    print(f"👉 Tip: Copy an image to '{USER_IMAGE_FOLDER}' and mention its filename to attach it.")
    
    while True:
        query = input("\nAsk a question about your PDFs (or 'exit'): ")
        if query.lower() == 'exit': break
        
        # Check for user images in query
        user_images_to_attach = []
        available_images = get_user_images()
        for img_name in available_images:
            if img_name in query:
                full_path = os.path.join(USER_IMAGE_FOLDER, img_name)
                print(f"📎 Attaching user image: {img_name}")
                try:
                    b64_img = encode_image(full_path)
                    user_images_to_attach.append(b64_img)
                except Exception as e:
                    print(f"⚠️ Failed to attach {img_name}: {e}")
        
        # Search the top 3 most relevant pages
        results = vectorstore.similarity_search(query, k=3)
        
        # Build context (Text and Images)
        context_text = ""
        context_images = []
        
        print("\n🔍 Retrieved Context:")
        for i, res in enumerate(results):
            data = json.loads(res.page_content)
            source_info = f"Source: {res.metadata.get('file', 'Unknown')}, Page: {res.metadata.get('page', 'Unknown')}"
            
            # Format text context
            snippet = f"\n--- Result {i+1} ({source_info}) ---\n{data.get('text', '')}\n"
            context_text += snippet
            
            # Handle images
            if 'image' in data:
                img_path = data['image']
                print(f"[Result {i+1}] {source_info} (Image: {img_path})")
                try:
                    b64_image = encode_image(img_path)
                    context_images.append(b64_image)
                except Exception as e:
                    print(f"⚠️ Failed to encode image {img_path}: {e}")
            else:
                print(f"[Result {i+1}] {source_info}")

        # Construct Payload for Azure
        # Simplify system prompt to avoid 'jailbreak' detection triggers
        system_prompt = "You are a helpful AI assistant."
        
        # User message logic: Text + Images
        user_content = []
        
        # Add text prompt with the instructions
        prompt_text = (
            "Please answer the question based on the provided context (text and images). "
            "If the user provided an image, include it in your analysis.\n\n"
            f"Context:\n{context_text}\n\nQuestion: {query}"
        )
        user_content.append({"type": "text", "text": prompt_text})
        
        # Add context images (from PDF)
        for b64 in context_images:
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64}"
                }
            })
            
        # Add user attached images
        for b64 in user_images_to_attach:
             user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64}"
                }
            })
            
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "max_tokens": 800,
            "temperature": 0.5
        }

        print(f"\n🤖 Calling Azure OpenAI (sending {len(context_images)} context images + {len(user_images_to_attach)} user images)...")
        
        try:
            response = requests.post(AZURE_ENDPOINT, headers=HEADERS, json=payload)
            response.raise_for_status()
            result = response.json()
            answer = result['choices'][0]['message']['content']
            print(f"\nAnswer: {answer}")
            
        except requests.exceptions.HTTPError as err:
            print(f"\n❌ API Error: {err}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    chat_with_docs()