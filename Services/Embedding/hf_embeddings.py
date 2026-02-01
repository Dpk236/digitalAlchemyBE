from huggingface_hub import InferenceClient
import os
import time
from typing import List
from langchain_core.embeddings import Embeddings

class HuggingFaceInferenceEmbeddings(Embeddings):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.client = InferenceClient(
            token=os.getenv("HF_TOKEN")
        )
        self.model_name = model_name

    def _get_embedding(self, texts: List[str]) -> List[List[float]]:
        for attempt in range(3):
            try:
                # Use the feature_extraction method
                embeddings = self.client.feature_extraction(
                    texts,
                    model=self.model_name
                )
                # Ensure it's a list (it might be a numpy array/tensor depending on version)
                if hasattr(embeddings, "tolist"):
                    return embeddings.tolist()
                return embeddings
            except Exception as e:
                if "503" in str(e) or "loading" in str(e).lower():
                    print("⌛ Hugging Face model loading... waiting 10s")
                    time.sleep(10)
                    continue
                raise e
        
        raise Exception("Hugging Face API failed after retries")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._get_embedding(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._get_embedding([text])[0]
