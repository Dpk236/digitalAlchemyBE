import os
import json
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow importing from PDFEmbedding
sys.path.append(str(Path(__file__).parent.parent))

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from VideoEmbedding.utils import LightEmbeddings

class VideoIngestor:
    def __init__(self, collection_name: str = "video_docs", qdrant_url: str = None, qdrant_api_key: str = None):
        self.collection_name = collection_name
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = qdrant_api_key or os.getenv("QDRANT_API_KEY", None)
        self.embeddings_model = LightEmbeddings()

    def ingest_directory(self, directory_path: str, subject: str = "Biology"):
        documents = []
        video_files = [f for f in os.listdir(directory_path) if f.endswith(".json")]

        for file_name in video_files:
            video_id = Path(file_name).stem
            file_path = os.path.join(directory_path, file_name)
            
            with open(file_path, "r") as f:
                data = json.load(f)
            
            print(f"📄 Processing {file_name} (Video ID: {video_id})...")
            
            for chunk in data:
                metadata = {
                    "video_id": video_id,
                    "subject": subject,
                    "start_time": chunk.get("start", 0),
                    "end_time": chunk.get("end", 0),
                    "chunk_id": chunk.get("id")
                }

                doc = Document(
                    page_content=chunk.get("text", ""),
                    metadata=metadata
                )
                documents.append(doc)

        if documents:
            print(f"📦 Indexing {len(documents)} chunks from {len(video_files)} videos into Qdrant...")
            QdrantVectorStore.from_documents(
                documents=documents,
                embedding=self.embeddings_model,
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
                collection_name=self.collection_name,
                force_recreate=True
            )
            print("✅ Ingestion complete.")
        else:
            print("⚠️ No documents found to ingest.")

if __name__ == "__main__":
    # Get the directory where the script is located
    current_dir = Path(__file__).parent
    ingestor = VideoIngestor()
    ingestor.ingest_directory(str(current_dir))
