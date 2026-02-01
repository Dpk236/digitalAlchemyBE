import re
import os
from Enums.explanation_mode_enum import ExplanationMode
from PyDantic.ResponseModel.intent_detect_model import IntentDetectModel
from constants.intent_confidence import CLARIFICATION_THRESHOLD
from store.openai_client import get_openai_client
from Helpers.QuizMemory.FetchQuizQuestion import get_quiz_question
from utility.quiz_explanation import extract_question_id
from query_enum import Intent

client = get_openai_client()
model = os.getenv("model")


TIME_REGEX = re.compile(
    r"""
    (?:
        \b\d{1,2}:\d{2}\b           |  # MM:SS or HH:MM
        \b\d{1,2}:\d{2}:\d{2}\b     |  # HH:MM:SS
        \b\d+\s*(?:min|mins|minute|minutes)\b
    )
    """,
    re.VERBOSE
)

def rule_based_detect_intent(user_query: str, chat_history=None, user_id=None, lecture_id=None, session_id=None) -> IntentDetectModel:
    query = user_query.lower()
    question_id = extract_question_id(query)
    isPresent = False

    if question_id is not None:
        quiz = get_quiz_question(
            user_id=user_id,
            lecture_id=lecture_id,
            session_id=session_id,
            question_id=question_id
        )
        if isinstance(quiz, dict) and "question_text" in quiz:
            isPresent = True

    # 1️⃣ Quiz explanation (VERY STRONG)
    if re.search(r"(explain|describe)\s+(question|q)\s*\d+", query):
        return IntentDetectModel(
            intent=Intent.EXPLAIN_QUIZ_QUESTION,
            confidence=0.95,
            source="rule",
            mode=ExplanationMode.STANDARD
        )

    if "question" in query and isPresent:
        return IntentDetectModel(
            intent=Intent.EXPLAIN_QUIZ_QUESTION,
            confidence=0.90,
            source="rule",
            mode=ExplanationMode.STANDARD
        )

    # 2️⃣ Timestamp intent
    if re.search(r"\b(\d+)\s*(min|minute|minutes)\b", query):
        return IntentDetectModel(
            intent=Intent.TIMESTAMP_QUERY,
            confidence=0.92,
            source="rule",
            mode=ExplanationMode.STANDARD
        )

    if TIME_REGEX.search(query):
        return IntentDetectModel(
            intent=Intent.TIMESTAMP_QUERY,
            confidence=0.85,
            source="rule",
            mode=ExplanationMode.STANDARD
        )

    # 3️⃣ Video summary
    if any(word in query for word in ["summarize", "summary", "summarise", "overview"]):
        return IntentDetectModel(
            intent=Intent.SUMMARIZE_VIDEO,
            confidence=0.90,
            source="rule",
            mode=ExplanationMode.STANDARD
        )

    if any(word in query for word in ["main points", "key points", "notes", "recap"]):
        return IntentDetectModel(
            intent=Intent.NOTES,
            confidence=0.87,
            source="rule",
            mode=ExplanationMode.STANDARD
        )

    # 4️⃣ Quiz generation
    if any(word in query for word in ["quiz", "mcq", "questions", "test", "practice"]):
        return IntentDetectModel(
            intent=Intent.QUIZ_GENERATION,
            confidence=0.88,
            source="rule",
            mode=ExplanationMode.STANDARD
        )
    if any(word in query for word in [
        "difference",
        "compare",
        "comparison",
        "vs",
        "versus",
        "which is better",
        "distinguish",
        "contrast",
        "differentiate",
        "How it is different",
        "How it differs",
    ]):
        print("Detected comparison intent")
        return IntentDetectModel(
            intent=Intent.CONTEXT_RETRIEVAL,
            confidence=0.65,
            source="rule",
            mode=ExplanationMode.COMPARISON
        )
    # 5️⃣ Weak explanation intent
    if any(word in query for word in ["explain", "why", "how", "what", "example", "which", "define", "meaning"]):
        return IntentDetectModel(
            intent=Intent.CONTEXT_RETRIEVAL,
            confidence=0.65,
            source="rule",
            mode=ExplanationMode.STANDARD
        )

    # 6️⃣ Fallback
    return IntentDetectModel(
        intent=Intent.FALLBACK,
        confidence=0.0,
        source="rule",
        mode=ExplanationMode.STANDARD
    )


def llm_classify_intent(user_query: str, chat_history=None) -> IntentDetectModel:
    system_prompt = """
    You are an intent classification engine.
    Analyze the user's query and determine their primary intent.

    Return the intent as one of the following options.
    CONTEXT_RETRIEVAL
    QUIZ_GENERATION
    EXPLAIN_QUIZ_QUESTION
    TIMESTAMP_QUERY
    SUMMARIZE_VIDEO
    NOTES
    FALLBACK
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0
    )

    intent_text = response.choices[0].message.content.strip()
    print("LLM intent_text:", intent_text)

    try:
        return IntentDetectModel(
            intent=Intent(intent_text),
            confidence=0.60,
            source="llm",
            mode=ExplanationMode.STANDARD
        )
    except ValueError:
        return IntentDetectModel(
            intent=Intent.FALLBACK,
            confidence=0.0,
            source="llm",
            mode=ExplanationMode.STANDARD
        )


def detect_intent(user_query: str, chat_history=None, user_id=None, lecture_id=None, session_id=None) -> IntentDetectModel:
    # 1️⃣ Rule-based detection (FAST)
    result = rule_based_detect_intent(user_query, chat_history, user_id, lecture_id, session_id)

    print("Rule-based intent:", result.intent)

    # 2️⃣ High confidence → accept immediately
    if result.confidence >= CLARIFICATION_THRESHOLD:
        return result

    # 3️⃣ Low confidence → use LLM fallback
    print("⚠️ Low confidence. Using LLM fallback.")
    llm_result = llm_classify_intent(user_query, chat_history)

    # 4️⃣ If LLM improves confidence → accept
    if llm_result.confidence > result.confidence:
        return llm_result

    # 5️⃣ Otherwise → fallback safely
    return IntentDetectModel(
        intent=Intent.FALLBACK,
        confidence=0.0,
        source="router",
        mode=ExplanationMode.STANDARD
    )
