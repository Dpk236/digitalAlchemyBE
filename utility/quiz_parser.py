from bs4 import BeautifulSoup
import re


def parse_quiz_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    questions = []

    for li in soup.find_all("li"):
        q = {
            "question_id": None,
            "question_text": None,
            "options": {},
            "correct_answer": None,
            "correct_answer_text": None,
            "timestamps": []
        }

        paragraphs = li.find_all("p")
        if not paragraphs:
            continue

        # -----------------------------
        # Question ID + Text
        # -----------------------------
        first_p = paragraphs[0].get_text(strip=True)

        match = re.match(r"Question\s*(\d+):\s*(.*)", first_p, re.IGNORECASE)
        if match:
            q["question_id"] = f"Q{match.group(1)}"
            q["question_text"] = match.group(2)

        # -----------------------------
        # Options
        # -----------------------------
        for p in paragraphs[1:]:
            text = p.get_text(strip=True)

            opt_match = re.match(r"([A-D])\.\s*(.*)", text)
            if opt_match:
                letter = opt_match.group(1)
                option_text = opt_match.group(2)
                q["options"][letter] = option_text

        # -----------------------------
        # Correct Answer + Timestamp
        # -----------------------------
        for p in paragraphs:
            if "Correct Answer" in p.get_text():
                text = p.get_text()

                ans_match = re.search(r"Correct Answer:\s*([A-D])", text)
                if ans_match:
                    q["correct_answer"] = ans_match.group(1)

                # Timestamp(s)
                for a in p.find_all("a"):
                    ts = a.get_text(strip=True).replace("(", "").replace(")", "")
                    q["timestamps"].append(ts)

        # -----------------------------
        # Correct Answer Text
        # -----------------------------
        if q["correct_answer"] and q["correct_answer"] in q["options"]:
            q["correct_answer_text"] = q["options"][q["correct_answer"]]

        # Final validation
        if q["question_id"] and q["question_text"]:
            questions.append(q)

    return questions
