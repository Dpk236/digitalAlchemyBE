import sys
from pathlib import Path

# Add the parent directory to sys.path to allow importing from PDFEmbedding
sys.path.append(str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from store.vector_store import embeddings

class VideoRetriever:
    def __init__(self, collection_name: str = "video_docs", qdrant_url: str = "http://localhost:6333"):
        self.collection_name = collection_name
        self.qdrant_url = qdrant_url
        self.embeddings_model = embeddings
        self.client = QdrantClient(url=qdrant_url)
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings_model
        )

    def search(self, query: str, k: int = 5):
        print(f"🔍 Searching for: '{query}'...")
        results = self.vector_store.similarity_search(query, k=k)
        
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "text": doc.page_content,
                "metadata": doc.metadata
            })
        return formatted_results

if __name__ == "__main__":
    retriever = VideoRetriever()
    query = "circulatory pathways and types of circulatory systems"
    results = retriever.search(query)
    
    print("\nTop Search Results:")
    for i, res in enumerate(results):
        print(f"\n[{i+1}] (Score: Not shown by similarity_search)")
        print(f"Video ID: {res['metadata'].get('video_id')}")
        print(f"Time: {res['metadata'].get('start_time')}s - {res['metadata'].get('end_time')}s")
        print(f"Text: {res['text'][:150]}...")
