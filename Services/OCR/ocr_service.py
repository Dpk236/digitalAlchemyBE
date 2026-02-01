import base64
import os
from store.openai_client import get_openai_client

class OCRService:
    def __init__(self):
        self.client = get_openai_client()
        self.model = os.getenv("model", "gpt-4o")

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def extract_text_from_image(self, base64_image: str) -> str:
        """
        Extracts question text from a base64 encoded image using GPT-4o.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract the question or educational text from this image. Only return the text of the question, nothing else."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
