from langchain_core.documents import Document


def reconstruct_langchain_doc(doc_data):
    try:
        # 4. Reconstruct LangChain Documents
        documents = []
        for p in doc_data:
            # LangChain stores the original page_content inside the payload
            content = p.payload.get("page_content", "")
            # The metadata dictionary is usually stored as a nested object
            meta = p.payload.get("metadata", p.payload)

            documents.append(Document(page_content=content, metadata=meta))

        # 5. Sort by timeline so the context is chronological
        documents.sort(key=lambda d: d.metadata.get("start_time", 0))
        return documents
    except Exception as e:
        print("Error reconstructing LangChain documents:", e)
        return []
