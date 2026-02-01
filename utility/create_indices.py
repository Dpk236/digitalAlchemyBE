import store.env_loader
from store.vector_store import get_qdrant_client
from qdrant_client import models

def create_indices():
    client = get_qdrant_client()
    collection_name = "ask_doubt_rag2"
    
    print("Creating indices for collection: " + collection_name)
    
    # Index for video_id (keyword)
    print("Creating index for metadata.video_id...")
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="metadata.video_id",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        print("Index request sent for metadata.video_id.")
    except Exception as e:
        print("Error creating index: " + str(e))

if __name__ == "__main__":
    create_indices()
