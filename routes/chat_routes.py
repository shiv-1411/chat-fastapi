from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic models for request/response validation
class ChatMessage(BaseModel):
    conversation_id: Optional[str] = None
    user_id: str
    message: str
    timestamp: datetime = datetime.now()

class ChatResponse(BaseModel):
    id: str
    conversation_id: str
    user_id: str
    message: str
    timestamp: datetime

# Temporary storage (replace with database later)
chat_messages = []
conversation_counter = 0

@router.post("/chats", response_model=ChatResponse, status_code=201)
async def store_chat_message(chat: ChatMessage):
    global conversation_counter
    conversation_counter += 1
    
    chat_data = chat.dict()
    chat_data["id"] = f"msg_{len(chat_messages) + 1}"
    chat_data["conversation_id"] = chat.conversation_id or f"conv_{conversation_counter}"
    
    chat_messages.append(chat_data)
    return chat_data

@router.get("/chats/{conversation_id}", response_model=List[ChatResponse])
async def get_conversation(conversation_id: str):
    conversation = [msg for msg in chat_messages if msg["conversation_id"] == conversation_id]
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.get("/users/{user_id}/chats", response_model=List[ChatResponse])
async def get_user_chats(
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    user_messages = [msg for msg in chat_messages if msg["user_id"] == user_id]
    
    # Simple pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated_messages = user_messages[start_idx:end_idx]
    return paginated_messages

@router.delete("/chats/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str):
    global chat_messages
    original_length = len(chat_messages)
    chat_messages = [msg for msg in chat_messages if msg["conversation_id"] != conversation_id]
    
    if len(chat_messages) == original_length:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return None 