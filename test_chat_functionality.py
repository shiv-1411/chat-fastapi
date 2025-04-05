import asyncio
import logging
from datetime import datetime
from config.database import Database
from services.summarizer import Summarizer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_chat_functionality():
    try:
        # Initialize database connection
        logger.info("Connecting to database...")
        await Database.connect_db()
        
        # Create test conversation
        conversation_id = "test_conversation_1"
        user_id = "test_user_1"
        
        # Test messages
        test_messages = [
            {
                "user_id": user_id,
                "message": "Hello, I'm interested in learning about AI.",
                "conversation_id": conversation_id,
                "timestamp": datetime.now()
            },
            {
                "user_id": "assistant",
                "message": "AI is a fascinating field! It involves creating intelligent machines that can perform tasks that typically require human intelligence.",
                "conversation_id": conversation_id,
                "timestamp": datetime.now()
            },
            {
                "user_id": user_id,
                "message": "What are some practical applications of AI?",
                "conversation_id": conversation_id,
                "timestamp": datetime.now()
            },
            {
                "user_id": "assistant",
                "message": "AI has many practical applications including natural language processing, computer vision, recommendation systems, and autonomous vehicles.",
                "conversation_id": conversation_id,
                "timestamp": datetime.now()
            }
        ]
        
        # Store test messages
        logger.info("Storing test messages...")
        for message in test_messages:
            await Database.store_message(message)
        
        # Retrieve conversation
        logger.info("Retrieving conversation...")
        messages = await Database.get_conversation(conversation_id)
        logger.info(f"Retrieved {len(messages)} messages")
        
        # Test summarization
        logger.info("Testing summarization...")
        summarizer = Summarizer()
        summary = await summarizer.summarize_conversation(conversation_id)
        logger.info("Generated summary:")
        logger.info(summary)
        
        # Clean up test data
        logger.info("Cleaning up test data...")
        await Database.delete_conversation(conversation_id)
        
        logger.info("✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        raise
    finally:
        # Close database connection
        await Database.close_db()

if __name__ == "__main__":
    asyncio.run(test_chat_functionality()) 