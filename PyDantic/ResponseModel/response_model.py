from typing import Any, Optional
from pydantic import BaseModel

class ChatResponse(BaseModel):
    type: str                 # e.g. "notes", "quiz", "answer", "error"
    ai_response: str          # formatted AI response (HTML / text)
    data: Optional[Any] = None  # extra payload (quiz JSON, metadata, etc.)
