from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import logging
from config.database import Database
from models.chat import ChatMessage, ChatResponse

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chats", response_model=ChatResponse)
async def create_message(message: ChatMessage):
    """Create a new chat message"""
    try:
        # Validate message content
        if not message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        if not message.user_id.strip():
            raise HTTPException(status_code=400, detail="User ID cannot be empty")
            
        # Generate conversation ID if not provided
        if not message.conversation_id:
            message.conversation_id = f"conv_{datetime.now().timestamp()}"
        
        # Prepare message data
        message_data = message.dict()
        message_data["timestamp"] = datetime.now().isoformat()
        
        # Store message in database
        message_id = await Database.store_message(message_data)
        logger.info(f"Created message with ID: {message_id}")
        
        return ChatResponse(
            id=message_id,
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            message=message.message,
            timestamp=message_data["timestamp"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chats/{conversation_id}", response_model=List[ChatResponse])
async def get_conversation(conversation_id: str):
    """Get all messages in a conversation"""
    try:
        # Validate conversation ID
        if not conversation_id.strip():
            raise HTTPException(status_code=400, detail="Conversation ID cannot be empty")
            
        messages = await Database.get_conversation(conversation_id)
        if not messages:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Convert MongoDB documents to response models
        responses = []
        for msg in messages:
            msg["id"] = str(msg.pop("_id"))
            responses.append(ChatResponse(**msg))
            
        return responses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/chats", response_model=List[ChatResponse])
async def get_user_messages(user_id: str):
    """Get all messages for a user"""
    try:
        # Validate user ID
        if not user_id.strip():
            raise HTTPException(status_code=400, detail="User ID cannot be empty")
            
        messages = await Database.get_user_messages(user_id)
        
        # Convert MongoDB documents to response models
        responses = []
        for msg in messages:
            msg["id"] = str(msg.pop("_id"))
            responses.append(ChatResponse(**msg))
            
        return responses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chats/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation and all its messages"""
    try:
        # Validate conversation ID
        if not conversation_id.strip():
            raise HTTPException(status_code=400, detail="Conversation ID cannot be empty")
            
        success = await Database.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 