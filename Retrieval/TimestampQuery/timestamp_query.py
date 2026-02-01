from qdrant_client.http.models import Filter, FieldCondition, Range

from utility.time_to_seconds import time_to_seconds
from utility.ReconstructLangChainDoc import reconstruct_langchain_doc
def retrieve_by_timestamp(
    vector_store,
    video_id: str,
    query: str,
    window_seconds: int = 245,
    limit: int = 200
):
    try:
            # 1. Ensure time_to_seconds logic is sound
        center_time = time_to_seconds(query)
        print("Parsed center time (s):", center_time)
        if center_time is None:
            raise ValueError(f"Could not parse timestamp from query: {query}")

        start = center_time
        end = center_time + window_seconds
        print(f"Searching for documents in video {center_time} from {start}s to {end}s")
        # 2. Use 'metadata.' prefix as LangChain nests these fields
        # Also ensuring video_id is treated as a string to match your data
        timestamp_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.video_id", 
                    match={"value": str(video_id)}
                ),
                # FieldCondition(
                #     key="metadata.start_time",
                #     range=Range(lte=end)
                # ),
                FieldCondition(
                    key="metadata.end_time",
                    range=Range(gte=start)
                )
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
            print(f"No documents found for video {video_id} between {start}-{end}s")
            return []
        return reconstruct_langchain_doc(results)
    except Exception as e:
        print("Error during timestamp-based retrieval:", e)
        return []

   