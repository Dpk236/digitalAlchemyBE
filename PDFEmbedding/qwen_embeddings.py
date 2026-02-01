import torch
import json
from typing import List, Union
from langchain_core.embeddings import Embeddings
from transformers import AutoModel, AutoProcessor
from qwen_vl_utils import process_vision_info

class Qwen3VLEmbeddings(Embeddings):
    def __init__(self, model_name: str = "Qwen/Qwen3-VL-Embedding-2B"):
        # Detect Mac GPU (MPS)
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Loading {model_name} on {self.device}...")
        
        # Load model and processor
        self.model = AutoModel.from_pretrained(
            model_name, 
            trust_remote_code=True, 
            torch_dtype=torch.float16
        ).to(self.device)
        self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        self.model.eval()

    def _get_embedding(self, input_data: List[dict]) -> List[float]:
        # Prepare inputs for the vision-language model
        messages = [[{"role": "user", "content": input_data}]]
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        
        inputs = self.processor(
            text=text,
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
            # Qwen3-VL-Embedding uses the hidden state of the last token (EOS pooling)
            last_hidden_state = outputs.hidden_states[-1]
            # Extract last non-padding token
            seq_len = inputs.attention_mask[0].sum()
            embedding = last_hidden_state[0, seq_len - 1]
            # Normalize for cosine similarity
            normalized_emb = torch.nn.functional.normalize(embedding, p=2, dim=0)
            return normalized_emb.cpu().numpy().tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            # Check if input is a JSON string containing image info
            try:
                data = json.loads(text)
                content = []
                if "image" in data: content.append({"type": "image", "image": data["image"]})
                if "text" in data: content.append({"type": "text", "text": data["text"]})
                embeddings.append(self._get_embedding(content))
            except (json.JSONDecodeError, TypeError):
                # Standard text input
                embeddings.append(self._get_embedding([{"type": "text", "text": text}]))
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]