import store.env_loader
from Services.Embedding.sentence_transform_embeddings import SentenceTransformerEmbeddings
from langchain_openai import OpenAIEmbeddings
from utility.reranker import rerank_documents
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
import os

# Embeddings
# embeddings = OpenAIEmbeddings(
#     model="text-embedding-3-small",
#     api_key="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"
# )
embeddings = SentenceTransformerEmbeddings()

# Qdrant client
qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
qdrant_api_key = os.getenv("QDRANT_API_KEY", None)

qdrant_client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key
)

from qdrant_client.http import models

# Ensure collection exists
try:
    if not qdrant_client.collection_exists("ask_doubt_rag2"):
        qdrant_client.create_collection(
            collection_name="ask_doubt_rag2",
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
        # Create Payload Index for video_id
        qdrant_client.create_payload_index(
            collection_name="ask_doubt_rag2",
            field_name="metadata.video_id",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        print("✅ Created new collection: ask_doubt_rag2")
except Exception as e:
    print(f"⚠️ Could not check/create collection: {e}")

# Vector store (connects to existing)
try:
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name="ask_doubt_rag2",
        embedding=embeddings,
    )
except Exception as e:
    print(f"⚠️ Vector Store Init Warning: {e}")
    vector_store = None

print("✅ Vector store ready:", vector_store)
def vector_store_ready() -> QdrantVectorStore:
    global vector_store
    if vector_store:
        return vector_store
    
    # Retry init
    try:
        vector_store = QdrantVectorStore(
            client=qdrant_client,
            collection_name="ask_doubt_rag2",
            embedding=embeddings,
        )
        return vector_store
    except Exception as e:
        print("VectorStore Error:", e)
        raise e


def get_qdrant_client() -> QdrantClient:
    return qdrant_client
