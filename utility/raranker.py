import json
from store.openai_client import get_openai_client
import os
client = get_openai_client()
model = os.getenv("model")
import re

def clean_llm_json(text: str) -> str:
    # Remove ```json, ``` and any leading/trailing whitespace
    text = text.strip()
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^```", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text

def rerank_documents(query: str, documents, top_k=3):
    """
    Uses LLM to score and rerank retrieved Qdrant chunks.
    Returns top_k best LangChain Documents.
    """
    print("documents", len(documents))
    # Build chunk list with timestamps
    chunk_text = ""
    for i, doc in enumerate(documents):
        start = doc.metadata.get("start_time")
        end = doc.metadata.get("end_time")
        text = doc.page_content.replace("\n", " ")
        chunk_text += f"[{i}] [{start}-{end}] {text}\n\n"

    print("chunk_text", chunk_text)

    prompt = f"""
    You are a relevance ranking engine.

    User question:
    "{query}"

    Below are transcript chunks from a lecture video.
    Each chunk has a timestamp.

    Score how relevant each chunk is to the question on a scale from 0 to 10.

    Return ONLY a valid JSON list in this format with any text in the response:
    [
    {{ "index": 0, "score": 8 }},
    {{ "index": 1, "score": 2 }}
    ]

    Chunks:
    {chunk_text}
    """

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": query}],
        temperature=0
    )
    print("AI response===", clean_llm_json(response.choices[0].message.content))
    try:
        scores = json.loads(clean_llm_json(response.choices[0].message.content))
    except Exception as e:
        # Safety fallback: if parsing fails, return first k
        print("exception involded over is", e)
        return documents[:top_k]

    # Sort by score
    ranked = sorted(scores, key=lambda x: x["score"], reverse=True)
    print("AI response=== ranked", ranked[:top_k])

    # Select top-k docs
    selected_docs = []
    for item in ranked[:top_k]:
        print("item ranked", item)
        selected_docs.append(documents[item["index"]])

    return selected_docs
