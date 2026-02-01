from store.openai_client import get_openai_client
from typing import Any
import os

model = os.getenv("model", "gpt-4o")
client = get_openai_client()


def get_summary(context: Any) -> str:
    print("Generating summary for chunk of type:", type(context))

    SYSTEM_PROMPT = f"""
    Act as a top NCERT tutor.
    Summarize this lecture segment strictly from the text only in perfect NCERT exam-preparation style.

    Lecture Segment Text:
    {context}

    Output format (use exactly):

    **Topic of this segment:** [one line]

    **Main Concept(s) Explained:**
    [2–4 short clear paragraphs]

    **Important Points to Remember:**
    • Bullet 1
    • Bullet 2
    • ...

    **Key Example(s) (if any):**
    1. ...

    **Most Important for Exams:** [one crisp sentence]
    About timestamps (very important):
     - If the content spans a range: <a href="#t=[start_time]-[end_time]">[MM:SS – MM:SS]</a>
    """
    print("Context injected into prompt successfully.")

    result_llm = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Please provide the summary as per the format."}
        ]
    )

    return result_llm.choices[0].message.content
