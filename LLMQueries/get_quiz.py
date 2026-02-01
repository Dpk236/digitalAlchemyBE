import os

from store.openai_client import get_openai_client
model = os.getenv("model", "gpt-4o")
client = get_openai_client()
def build_quiz_prompt(video_summary: str) -> str:
    print("video_summaryvideo_summary", len(video_summary))
    json_structure = {
        "quiz_title": "<short title based on lecture topic>",
        "total_questions": 8,
        "questions": [
            {
            "id": 1,
            "question_text": "...",
            "options": {
                "A": "...",
                "B": "...",
                "C": "...",
                "D": "..."
            },
            "correct_option": "C",
            "hint": "...",
            "explanation": "...",
            "solution": "..."
            }
        ]
        }
    prompt = f"""
        You are an expert NCERT-based educational assessment generator.

        Your task:
        Analyze the provided LECTURE SUMMARY and generate a high-quality quiz.

        GOAL:
        Create the TOP 8 most important multiple-choice questions that best test a student’s understanding of the lecture.

        SELECTION RULES (VERY IMPORTANT):
        - Questions MUST be derived ONLY from the given summary
        - Focus on:
        - Core definitions
        - Key characteristics
        - Important examples
        - Frequently tested concepts
        - Conceptual clarity (not trivial facts)
        - Prefer concepts emphasized or repeated in the summary
        - Do NOT add external knowledge
        - Do NOT invent facts
        - Use NCERT terminology strictly

        QUESTION REQUIREMENTS:
        Each question MUST include:
        1. question_text
        2. 4 options (A, B, C, D)
        3. correct_option (A/B/C/D)
        4. hint (short clue, NOT the answer)
        5. explanation (2–3 lines, student-friendly, NCERT-aligned)
        6. solution (direct, concise justification of the correct answer)

        DIFFICULTY MIX:
        - 3 easy
        - 3 medium
        - 2 conceptual / reasoning-based

        STYLE:
        - Clear and exam-oriented
        - Avoid ambiguity
        - Avoid negative framing unless required
        - Language: simple, precise, student-friendly

        OUTPUT FORMAT (MANDATORY):
        - Return ONLY valid JSON
        - No markdown
        - No extra text
        - No comments

        JSON STRUCTURE:
        {json_structure}

        If the summary does not contain enough information for 8 questions, generate as many as possible and clearly reduce total_questions accordingly.

        LECTURE SUMMARY:
        {video_summary}
        """

    return prompt

def get_quiz(video_summary):
    prompt = build_quiz_prompt(video_summary)
    print("promptprompt", prompt)
    result_llm = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Generate the Quiz"}
        ]
    )

    raw_data = result_llm.choices[0].message.content
    print("Raw LLM Data generated.", raw_data)
    return raw_data