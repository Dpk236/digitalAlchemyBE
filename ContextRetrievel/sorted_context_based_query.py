from ast import Dict
from typing import Any, Optional
from pydantic import BaseModel, Field
from store.vector_store import vector_store_ready
vector_store = vector_store_ready()
class SortedContextBasedQuery(BaseModel):
    """Provides the sorted context from vector db based on query and limit"""

    query: str = Field(
        ..., description="String user query for search"
    )

    topK: Optional[int] = Field(
        6, description="Maximum number of results to fetch"
    )
    video_filter: Optional[Any] = Field(
        None, description = "Optional video filter condition"
    )
    def sorted_context_query(self):
        query = self.query
        topK = self.topK
        video_filter = self.video_filter
        search_result = vector_store.similarity_search(
            query=query,
            k=topK,
            filter=video_filter,
        )
        # print("Search Result:", len(search_result), chat_history)
        docs_sorted = sorted(
            search_result,
            key=lambda d: d.metadata.get("start_time", 0)
        )
        return docs_sorted
