from fastapi import APIRouter, HTTPException
from services.summarizer import Summarizer
from models.summary import SummaryRequest, SummaryResponse
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()
summarizer = Summarizer()

@router.post("/summarize", response_model=SummaryResponse)
async def create_summary(request: SummaryRequest):
    """Create a summary for a conversation"""
    try:
        logger.info("Received summary request for conversation: %s", request.conversation_id)
        
        summary = await summarizer.summarize_conversation(
            request.conversation_id,
            request.max_length
        )
        
        response = SummaryResponse(
            conversation_id=request.conversation_id,
            summary=summary,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info("Successfully created summary for conversation: %s", request.conversation_id)
        return response
        
    except ValueError as e:
        logger.error("Validation error: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error creating summary: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e)) 