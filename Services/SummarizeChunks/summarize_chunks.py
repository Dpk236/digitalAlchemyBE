
import json
from typing import List, Dict
from Services.SummarizeChunks.parallel_map_chunk import ParallelMapChunk
from utility.combine_transcript_by_interval import combine_transcript_by_interval


from Retrieval.SummarizeQuery.SummarizeQuery import retrieve_all_chunks_by_video_id
from store.vector_store import vector_store_ready

def SummarizeChunks(video_id: str):
    """Summarize chunks in parallel using vector store data."""
    print(f"🔄 Starting summary generation for video: {video_id}")
    new_docs = retrieve_all_chunks_by_video_id(
        vector_store=vector_store_ready(),
        video_id=video_id,
    )
    
    if not new_docs:
        print(f"⚠️ No chunks found for video {video_id} in vector store.")
        return
        
    ParallelMapChunk(
        video_id=video_id,
        chunks=new_docs,
    )
    # read chunks and summarize them in parallel
    pass
