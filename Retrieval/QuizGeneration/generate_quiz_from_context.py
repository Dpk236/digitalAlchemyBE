import store.env_loader
import os
from store.openai_client import get_openai_client

model = os.getenv("model", "gpt-4o")
def generate_quiz_from_context(query: str, context: str):
    print("Generating quiz from context...", query, context)
    openai_connection = get_openai_client()
    system_prompt = f"""
    You are an expert quiz generator. Based on the user query and the provided context from a lecture video, generate a quiz that tests the user's understanding of the topic.

    Context:
    {context}

    User Query:
    {query}
    Rules:
    - Answer ONLY using the provided CONTEXT.
    - Do NOT add external knowledge.
    - If context is insufficient, say so clearly.
    - Do NOT hallucinate.
    - Maintain NCERT terminology.
    - Respond in the user’s language.
    - Mention timestamps only if present in context.
    Instructions:
    - Create 5 multiple-choice questions related to the context.
    - Each question should have 4 options (A, B, C, D).
    - Clearly indicate the correct answer for each question.
    - Ensure questions vary in difficulty and cover different aspects of the context.

    Style:
    - Clear, concise explanations.
    - Bullet points when helpful.
    - Add space between questions for readability.

    FORMAT RULES (MANDATORY):
    - Output MUST be valid HTML.
    - Wrap ALL questions inside ONE <ul>.
    - Each question MUST be inside ONE <li>.
    - Inside each <li>, use ONLY <p> tags.
    - Question line MUST be exactly:
    <p><b>Question X:</b> Question text</p>
    - Options MUST be exactly:
    <p>A. option text</p>
    <p>B. option text</p>
    <p>C. option text</p>
    <p>D. option text</p>
    - Correct answer MUST be exactly:
    <p><b>Correct Answer:</b> X <a href="timestamp_link">HH:MM:SS</a></p>
    - Do NOT include <html>, <body>, <head> tags.
    - Do NOT include explanations.
    - Do NOT add extra text outside <ul>.

    """

    result_llm = openai_connection.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": query
            }
        ]
    )
    quiz_data = result_llm.choices[0].message.content
    return quiz_data