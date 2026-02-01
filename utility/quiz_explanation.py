# handlers/quiz_explanation.py

import re
def extract_question_id(user_query: str) -> str | None:
    """
    Extracts Question number from queries like:
    - Explain Question 4
    - Explain Q4
    - Explain question number 4
    """
    match = re.search(r"(question|q)\s*(\d+)", user_query.lower())
    if not match:
        return None
    return f"Q{match.group(2)}"
