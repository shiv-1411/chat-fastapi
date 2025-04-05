from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId

class ChatMessage(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    conversation_id: str
    user_id: str
    message: str
    timestamp: str

    class Config:
        json_encoders = {
            ObjectId: str
        }
        populate_by_name = True 