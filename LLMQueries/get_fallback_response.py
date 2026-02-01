from email import message
from pyexpat.errors import messages
from store.openai_client import get_openai_client
from typing import Any
import os
model = os.getenv("model", "gpt-4o")
client = get_openai_client()


def get_fallback_response_query(query: str, context: Any, chat_history, summary) -> str:
    SYSTEM_PROMPT = f"""
    You are an chat history anyliser.
    TASK:
    You need to provide a concise and relevant answer to the user's question based on the provided context.
    You will get user chathistory as context.

    RULES:
    - Use ONLY the provided context.
    - Do NOT add external knowledge.
    - Provide the some counter questions to understand the user's needs better.
    
    Output rules (strict):
    - Return ONLY valid HTML content (wrap everything inside <html><body>...</body></html>)
    - Use <b>bold</b>, <i>italics</i>, <ul><li>lists</li></ul> ONLY when it genuinely helps clarity (examples, steps, comparisons)
    - Never use markdown, plain text outside HTML, or other tags
    - Never give full lecture summaries unless explicitly asked
    CONTEXT:
    {context}

    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]
    if summary:
        messages.append({
            "role": "system",
            "content": f"Conversation summary so far:\n{summary}"
        })
    messages.extend(chat_history)

    result_llm = client.chat.completions.create(
        model=model,
        messages=messages
    )

    raw_data = result_llm.choices[0].message.content
    # print("Raw LLM Data:", raw_data)
    return raw_data
