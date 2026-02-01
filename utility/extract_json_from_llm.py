import json
import re

def extract_json_from_llm(text: str) -> dict:
    """
    Extracts and parses JSON from an LLM response safely.
    Handles markdown code blocks and extra text.
    """
    # Remove ```json and ``` if present
    cleaned = re.sub(r"```json|```", "", text).strip()

    # Extract JSON object using regex
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("❌ No JSON object found in LLM response")

    json_str = match.group(0)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ Invalid JSON format: {e}")

def save_quiz_locally(llm_response: str, file_path=""):
    if file_path == "":
        return
    quiz_data = extract_json_from_llm(llm_response)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(quiz_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Quiz saved successfully to {file_path}")
    return quiz_data
