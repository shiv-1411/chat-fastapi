from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SummaryRequest(BaseModel):
    conversation_id: str
    max_length: Optional[int] = 150

class SummaryResponse(BaseModel):
    conversation_id: str
    summary: str
    timestamp: str 