from store.openai_client import get_openai_client
from typing import Any
import os
model = os.getenv("model", "gpt-4o")
client = get_openai_client()
def get_notes_query(user_query: str, context: Any) -> str:
    SYSTEM_PROMPT = f"""
    You are an NCERT-based AI Teaching Assistant.
    TASK:
    Create concise, student-friendly NOTES from the given video context.

    RULES:
    - Use ONLY the provided context.
    - Do NOT add external knowledge.
    - Do NOT explain beyond what is stated.
    - Keep points short and exam-oriented.
    - Maintain NCERT terminology.
    - Avoid unnecessary words.

    FORMAT:
    - Return the ouput in HTML format like html,body tag
    - Use <b> for bold, <i> for italics, <ul></ul> and <li> for lists.
    - No markdown, plain text, or other HTML tags.
    - Use short headings and bullet points.
    - Mention timestamps in (MM:SS) format.
    - Follow the structure shown in the example.

    STRUCTURE:
    1. One-line overview of the video topic
    2. Key concept/formula (if any)
    3. Step-by-step derivation or explanation (bullets)
    4. Examples (numbered, very brief)

    CONTEXT:
    {context}

    """

    result_llm = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ]
    )

    raw_data = result_llm.choices[0].message.content
    # print("Raw LLM Data:", raw_data)
    return raw_data
