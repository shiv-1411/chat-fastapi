from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from config.database import chat_messages, get_next_conversation_id, get_next_message_id
from services.summarization import SummarizationService
from bson import ObjectId

router = APIRouter()
summarization_service = SummarizationService()

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

@router.post("/chats", response_model=ChatResponse, status_code=201)
def store_chat_message(chat: ChatMessage):
    """Store a new chat message"""
    chat_data = chat.dict()
    chat_data["id"] = get_next_message_id()
    chat_data["conversation_id"] = chat.conversation_id or get_next_conversation_id()
    
    chat_messages.append(chat_data)
    return chat_data

@router.get("/chats/{conversation_id}", response_model=List[ChatResponse])
def get_conversation(conversation_id: str):
    """Get all messages in a specific conversation"""
    conversation = [msg for msg in chat_messages if msg["conversation_id"] == conversation_id]
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.get("/users/{user_id}/chats", response_model=List[ChatResponse])
def get_user_chats(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page")
):
    """
    Get paginated chat history for a specific user
    - page: Page number (starts from 1)
    - limit: Number of items per page (max 100)
    """
    # Filter messages for the specific user
    user_messages = [msg for msg in chat_messages if msg["user_id"] == user_id]
    
    # Calculate pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    # Get paginated messages
    paginated_messages = user_messages[start_idx:end_idx]
    
    # If no messages found and page > 1, raise 404
    if not paginated_messages and page > 1:
        raise HTTPException(status_code=404, detail="No more messages found")
    
    return paginated_messages

@router.delete("/chats/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str):
    """Delete an entire conversation"""
    global chat_messages
    original_length = len(chat_messages)
    
    # Remove all messages from the specified conversation
    chat_messages = [msg for msg in chat_messages if msg["conversation_id"] != conversation_id]
    
    # If no messages were deleted, the conversation doesn't exist
    if len(chat_messages) == original_length:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return None

@router.post("/chats/summarize/{conversation_id}")
async def summarize_conversation(conversation_id: str):
    """Generate a summary of a specific conversation using LLM"""
    cursor = chat_messages.find({"conversation_id": conversation_id})
    messages = await cursor.to_list(length=None)
    
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    summary = await summarization_service.generate_summary(messages)
    if summary.get("status") == "error":
        raise HTTPException(status_code=500, detail=summary.get("error"))
    
    return summary 