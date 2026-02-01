import re
from qdrant_client.http.models import Filter, FieldCondition, Range
from utility.ReconstructLangChainDoc import reconstruct_langchain_doc
from qdrant_client.http.models import Filter, FieldCondition
from utility.ReconstructLangChainDoc import reconstruct_langchain_doc
def retrieve_by_summarize_query(
    vector_store,
    video_id: str,
    limit: int = 200
):
    try:
            # 1. Ensure time_to_seconds logic is sound
        start = 0
        timestamp_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.video_id", 
                    match={"value": str(video_id)}
                ),
                
            ]
        )

        # 3. Execute scroll
        results, _ = vector_store.client.scroll(
            collection_name=vector_store.collection_name,
            scroll_filter=timestamp_filter,
            limit=limit,
            with_payload=True
        )

        if not results:
            print(f"No documents found for video {video_id}")
            return []
        print("Results found:", results[0].payload)
        return reconstruct_langchain_doc(results)
    except Exception as e:
        print("Error during timestamp-based retrieval:", e)
        return []



def retrieve_all_chunks_by_video_id(
    vector_store,
    video_id: str,
    batch_size: int = 100
):
    try:
        all_results = []
        offset = None

        video_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.video_id",
                    match={"value": str(video_id)}
                )
            ]
        )

        while True:
            results, offset = vector_store.client.scroll(
                collection_name=vector_store.collection_name,
                scroll_filter=video_filter,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            
            if not results:
                break
                
            print(f"Adding batch of {len(results)} chunks")
            all_results.extend(results)

            if offset is None:
                break

        if not all_results:
            print(f"No documents found for video_id={video_id}")
            return []

        print(f"Fetched {len(all_results)} chunks for video {video_id}")

        # Convert Qdrant points → LangChain Documents
        docs = reconstruct_langchain_doc(all_results)

        # Ensure correct order (VERY IMPORTANT)
        docs.sort(key=lambda d: d.metadata.get("start_time", 0))

        return docs

    except Exception as e:
        print("Error fetching chunks:", e)
        return []


def fetch_all_chunks_from_qdrant(vector_store, video_id: str):
    all_docs = []
    offset = None

    while True:
        docs, offset = vector_store.client.scroll(
            collection_name=vector_store.collection_name,
            limit=100,
            offset=offset,
            filter={
                "must": [
                    {
                        "key": "video_id",
                        "match": {"value": video_id}
                    }
                ]
            }
        )

        if not docs:
            break

        all_docs.extend(docs)

        if offset is None:
            break

    return sorted(
        [
            {
                "video_id": d.payload["video_id"],
                "start_time": d.payload["start_time"],
                "end_time": d.payload["end_time"],
                "text": d.payload["text_original"]
            }
            for d in all_docs
        ],
        key=lambda x: x["start_time"]
    )
