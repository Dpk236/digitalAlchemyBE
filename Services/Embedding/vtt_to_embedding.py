from Services.Embedding.sentence_transform_embeddings import SentenceTransformerEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document

# Initialize embedding model
embeddings = SentenceTransformerEmbeddings()

# Qdrant (local, in-memory or disk)
client = QdrantClient(path="./qdrant_data")

COLLECTION_NAME = "video_transcripts"

# Parse transcript
docs_raw = parse_vtt(
    file_path="/mnt/data/Bio480989616.vtt",
    video_id="480989616"
)

# Convert to LangChain Documents
documents = [
    Document(
        page_content=d["page_content"],
        metadata=d["metadata"]
    )
    for d in docs_raw
]

# Create vector store
vectorstore = QdrantVectorStore.from_documents(
    documents=documents,
    embedding=embeddings,
    url=None,
    client=client,
    collection_name=COLLECTION_NAME
)

print(f"Stored {len(documents)} transcript chunks")
