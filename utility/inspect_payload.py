from store.vector_store import get_qdrant_client

def inspect_payload():
    client = get_qdrant_client()
    collection_name = "ask_doubt_rag2"
    
    # Scroll to get 1 point
    res = client.scroll(
        collection_name=collection_name,
        limit=1,
        with_payload=True
    )
    
    points, _ = res
    if points:
        print("✅ Found point:")
        print(points[0].payload)
    else:
        print("❌ Collection is empty or no points found.")

if __name__ == "__main__":
    inspect_payload()
