# from typing import List
# from sentence_transformers import SentenceTransformer
# from langchain_core.embeddings import Embeddings

# class LightEmbeddings(Embeddings):
#     def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
#         print(f"Loading {model_name}...")
#         self.model = SentenceTransformer(model_name)

#     def embed_documents(self, texts: List[str]) -> List[List[float]]:
#         return self.model.encode(texts).tolist()

#     def embed_query(self, text: str) -> List[float]:
#         return self.model.encode([text])[0].tolist()
