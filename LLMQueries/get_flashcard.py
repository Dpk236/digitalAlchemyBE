from store.openai_client import get_openai_client
from typing import Any
import os
model = os.getenv("model", "gpt-4o")
client = get_openai_client()
from pathlib import Path
OUTPUT_FILE = "aiflashcard.html"

# ---------------- PROMPT ---------------- #

def build_canvas_prompt(video_summary: str) -> str:
    return f"""
You are an AI Teaching Assistant specialized in creating flashcards for NCERT-based students.

Your task:
- Create high-quality study flashcards strictly using the provided LECTURE SUMMARY.
- The flashcards should help students revise concepts quickly and effectively.

INPUT:
- You will be given a LECTURE SUMMARY derived from a video lecture.
- The summary may include definitions, explanations, examples, and exam-focused points.
- The summary may also include timestamps indicating where the topic is discussed.

RULES (MANDATORY):
1. Use ONLY the information provided in the LECTURE SUMMARY.
2. Do NOT add external knowledge or facts.
3. Do NOT assume anything that is not explicitly stated.
4. If some information is unclear or incomplete, skip creating a flashcard for it.
5. Maintain NCERT terminology and school-level accuracy.
6. Keep the language simple and student-friendly.
7. Do NOT include irrelevant or conversational content.

FLASHCARD GUIDELINES:
- Each flashcard must have:
  - A clear **Question (Front side)**
  - A concise **Answer (Back side)**
- Focus on:
  - Definitions
  - Key characteristics
  - Important examples
  - Exam-relevant points
- Avoid long paragraphs; answers should be short and precise.
- Prefer “What is…”, “Define…”, “Give one example…”, “State one function…” types of questions.

TIMESTAMP HANDLING:
- If a timestamp is present in the summary, attach it to the flashcard.
- Format timestamps as: HH:MM:SS
- Include timestamps only if they are explicitly mentioned.

OUTPUT FORMAT (STRICT):
Return the output as a JSON array in the following format:
  "question": "Flashcard question here",
    "answer": "Short and clear answer here",
    "timestamp": "HH:MM:SS (optional)"
IMPORTANT:
- Do NOT include explanations outside the flashcards.
- Do NOT include markdown, HTML, or extra text.
- Return ONLY valid JSON.

Summary content:{video_summary}
"""

# ---------------- GEMINI CALL ---------------- #

def generate_simulator(video_summary: str) -> str:
    result_llm = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": build_canvas_prompt(video_summary)},
            {"role": "user", "content": "Generate the simulator HTML file."}
        ]
    )

    raw_data = result_llm.choices[0].message.content
    print("Raw LLM Data generated.")
    return raw_data


# ---------------- SAVE FILE ---------------- #

def save_html(content: str):
    Path(OUTPUT_FILE).write_text(content, encoding="utf-8")
    print(f"✅ Simulator generated: {OUTPUT_FILE}")


# ---------------- MAIN ---------------- #

def get_flashcard_query(summary: str) -> str:
    print("\n⏳ Generating interactive simulator...\n")
    html_output = generate_simulator(summary)

    save_html(html_output)
    return html_output
