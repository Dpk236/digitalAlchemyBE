from pydantic import BaseModel, Field


class IntentDetectModel(BaseModel):
    """
    Model to represent the detected intent from a user query.
    """
    # e.g. "explain_quiz_question", "timestamp_query", etc.
    intent: str = Field(..., description="Detected intent of the user query")
    confidence: float = Field(...,
                              description="confidence score between 0 and 1")
    source: str = Field(..., description="e.g. rule, ml_model, etc.")
    #
    mode: str = Field(..., description="e.g. standard, comparison, etc.")
