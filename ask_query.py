import store.env_loader
import os
from typing import Any
from Enums.explanation_mode_enum import ExplanationMode
from langchain_core.documents import Document

from store.openai_client import get_openai_client
model = os.getenv("model", "gpt-4o")
client = get_openai_client()


def documents_to_json(documents: list[Document]) -> list[dict]:
    json_docs = []

    for doc in documents:
        json_docs.append({
            "content": doc.page_content,
            "metadata": {
                key: value
                for key, value in doc.metadata.items()
                if not key.startswith("_")   # remove internal qdrant keys
            }
        })

    return json_docs


def get_user_query(user_query: str, context: Any, chat_history: Any, explanation_mode=ExplanationMode.STANDARD, summary: str="") -> str:
    SYSTEM_PROMPT = f"""
    You are an excellent, patient NCERT-based AI Teaching Assistant who teaches exactly like a very good Indian school teacher explaining a recorded lecture to a Class 8–12 student.

    Core behavior:
    - Speak naturally, conversationally, like you're sitting next to the student
    - Use short paragraphs — explain step-by-step, building understanding gradually
    - Use simple, clear language — avoid sounding like a textbook or bullet-point notes
    - Be encouraging and supportive without being over-the-top
    - Use examples from the lecture when they help understanding
    - Maintain perfect fidelity to NCERT terminology and explanations — never add external knowledge
    - ALWAYS stay strictly within the provided CONTEXT only

    Output rules (strict):
    STRUCTURE RULES:
    - Use headings (##, ###) for sections
    - Use short paragraphs (max 2–3 lines)
    - Use bullet points where possible
    - Highlight key conclusions using **bold**
    - Always keep timestamps inline as [MM:SS]


    When the question is comparative ("compare X and Y", "difference between...", "X vs Y"):
    - First give a short neutral introduction to both concepts
    - Then explain differences clearly — preferably in a small table or side-by-side paragraphs
    - Use lecture examples to illustrate
    - Never say one is better unless the lecture itself clearly states it

    Answer structure philosophy (follow this spirit, NOT as rigid points):
    1. Start with a short, friendly rephrasing of what the student is asking + quick big-picture orientation
    2. Explain the concept progressively, as if teaching it live
    3. Bring in 1–2 relevant examples from the lecture when helpful
    4. End with a short summary sentence + (if natural) a gentle question to check understanding

    Rules — never break these:
    - Answer ONLY using the provided CONTEXT. If something is not mentioned → reply only: "context does not contain" stick this phrase
    - Do NOT hallucinate, do NOT add outside knowledge, even if it is common NCERT knowledge not present in this specific lecture
    - Keep explanations connected and flowing — avoid mechanical lists
    - Use chat history to remember what was already explained to the same student
    """
    if explanation_mode == ExplanationMode.COMPARISON.value:
        SYSTEM_PROMPT += """
        The question is a comparison-based question.

        Instructions:
        - Explain differences point-wise or side-by-side.
        - Do NOT say one is better unless the lecture explicitly says so.
        - Use examples from the CONTEXT to illustrate differences.
        Example Structure:
        1. Introduction to both concepts.
        2. Key Differences:
            - Point 1: Explanation with examples.
            - Point 2: Explanation with examples.
        3. Conclusion summarizing the comparison.
        """
    messages = []
    # 1️⃣ System prompt (rules only)
    messages.append({
        "role": "system",
        "content": SYSTEM_PROMPT
    })
    if summary:
        messages.append({
            "role": "system",
            "content": f"Conversation summary so far:\n{summary}"
        })
    # 2️⃣ Chat history (last 4–6 messages)
    if len(chat_history) > 0:
        messages.extend(chat_history)

    # 3️⃣ Current user message (with context)
    messages.append({
        "role": "user",
        "content": f"""
    Use the following CONTEXT to answer the question.

    CONTEXT:
    {context}

    QUESTION:
    {user_query}
    """
    })

    # print("Model used:", messages)
    result_llm = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2
    )
    raw_data = result_llm.choices[0].message.content
    # print("Raw LLM Data:", raw_data)
    return raw_data
