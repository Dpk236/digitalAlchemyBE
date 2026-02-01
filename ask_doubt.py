
import json
import os
import store.env_loader
from store.vector_store import embeddings
from convert_vtt_json import vtt_to_segments
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document

# embeddings = SentenceTransformerEmbeddings("all-MiniLM-L6-v2") # Replaced by API-based embeddings

def semantic_chunk_segments(
    segments: list[dict],
    min_words: int = 40,
    max_words: int = 120
) -> list[dict]:
    chunks = []

    current_text = []
    start_time = None
    end_time = None

    for seg in segments:
        text = seg["text_original"].strip()
        if not text:
            continue

        if start_time is None:
            start_time = seg["start_time"]

        current_text.append(text)
        end_time = seg["end_time"]

        word_count = len(" ".join(current_text).split())

        # create chunk when enough content
        if word_count >= min_words:
            chunks.append({
                **seg,
                "start_time": start_time,
                "end_time": end_time,
                "text_original": " ".join(current_text)
            })

            # reset
            current_text = []
            start_time = None
            end_time = None

        # safety cap
        if word_count >= max_words:
            current_text = []
            start_time = None
            end_time = None

    return chunks


def build_documents(chunks: list[dict]) -> list[Document]:
    documents = []

    for chunk in chunks:
        # Skip weak chunks
        if len(chunk["text_original"].split()) < 30:
            continue

        metadata = {
            "video_id": chunk.get("video_id"),
            "subject": chunk.get("subject"),
            "chapter": chunk.get("chapter"),
            "start_time": chunk.get("start_time", 0),
            "end_time": chunk.get("end_time", 0),
        }

        documents.append(
            Document(
                page_content=chunk["text_original"],
                metadata=metadata
            )
        )

    return documents


def ingest_transcript(file_path: str, video_id: str = None, subject: str = None, chapter: str = None):
    print(f"📄 Processing transcript: {file_path}...")
    
    if file_path.endswith(".vtt"):
        segments = vtt_to_segments(file_path)
    elif file_path.endswith(".json"):
        with open(file_path, "r") as f:
            data = json.load(f)
            
            # Support for both flat array and new nested structure
            if isinstance(data, dict) and "segments" in data:
                raw_segments = data["segments"]
                video_id = data.get("video_id", video_id)
                subject = data.get("subject", subject)
                chapter = data.get("chapter", chapter)
            else:
                raw_segments = data

            segments = [{
                "video_id": video_id,
                "subject": subject,
                "chapter": chapter,
                "start_time": item.get("start", 0),
                "end_time": item.get("end", 0),
                "text_original": item.get("text", "")
            } for item in raw_segments]
    else:
        print("❌ Unsupported format. Use .vtt or .json")
        return

    semantic_chunks = semantic_chunk_segments(segments)
    documents = build_documents(semantic_chunks)
    
    print(f"📦 Indexing {len(documents)} chunks for '{chapter or video_id}' into Qdrant...")
    QdrantVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY", None),
        collection_name="ask_doubt_rag2"
    )
    print(f"✅ Ingestion complete for {file_path}.")

def bulk_ingest_transcripts(directory_path: str):
    import os
    print(f"📁 Bulk ingesting transcripts from: {directory_path}...")
    for filename in os.listdir(directory_path):
        if filename.endswith(".json") or filename.endswith(".vtt"):
            ingest_transcript(os.path.join(directory_path, filename))

if __name__ == "__main__":
    # To bulk ingest everything in the transcript folder:
    bulk_ingest_transcripts("transcript")

    # print("VTT to Qdrant Vector DB conversion completed.")
