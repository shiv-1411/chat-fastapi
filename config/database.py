from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is not set")

DATABASE_NAME = os.getenv("MONGODB_DB", "chat_db")
MESSAGES_COLLECTION = "messages"

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_db(cls) -> None:
        """Connect to MongoDB"""
        try:
            logger.info("Connecting to MongoDB Atlas")
            
            # Configure MongoDB client with basic settings
            cls.client = AsyncIOMotorClient(
                MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=0,
                tls=True,
                tlsAllowInvalidCertificates=True
            )
            
            logger.info("Client created, attempting to access database...")
            cls.db = cls.client[DATABASE_NAME]
            
            # Verify connection with a simple command
            logger.info("Verifying connection with ping command...")
            await cls.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB Atlas!")
            
            # Create indexes
            logger.info("Creating database indexes...")
            collection = cls.db[MESSAGES_COLLECTION]
            await collection.create_index("user_id")
            await collection.create_index("conversation_id")
            logger.info("✅ Database indexes created")
            
        except Exception as e:
            logger.error(f"❌ MongoDB Connection Error: {str(e)}")
            if cls.client:
                cls.client.close()
                cls.client = None
                cls.db = None
            raise

    @classmethod
    async def close_db(cls) -> None:
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("Closed MongoDB connection")

    @classmethod
    async def get_messages_collection(cls):
        """Get messages collection"""
        if cls.db is None:
            await cls.connect_db()
        return cls.db[MESSAGES_COLLECTION]

    @classmethod
    async def store_message(cls, message_data: Dict[str, Any]) -> str:
        """Store a new message"""
        try:
            # Validate required fields
            required_fields = ["user_id", "message", "conversation_id", "timestamp"]
            missing_fields = [field for field in required_fields if field not in message_data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            collection = await cls.get_messages_collection()
            result = await collection.insert_one(message_data)
            logger.info(f"✅ Message stored with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"❌ Error storing message: {str(e)}")
            raise

    @classmethod
    async def get_conversation(cls, conversation_id: str) -> List[Dict[str, Any]]:
        """Get messages for a specific conversation"""
        try:
            # Validate conversation ID
            if not conversation_id:
                raise ValueError("Conversation ID cannot be empty")

            collection = await cls.get_messages_collection()
            cursor = collection.find({"conversation_id": conversation_id})
            messages = await cursor.to_list(length=None)
            
            # Convert datetime objects to ISO format strings
            for msg in messages:
                if isinstance(msg.get("timestamp"), datetime):
                    msg["timestamp"] = msg["timestamp"].isoformat()
                    
            logger.info(f"✅ Retrieved {len(messages)} messages for conversation {conversation_id}")
            return messages
        except Exception as e:
            logger.error(f"❌ Error getting conversation: {str(e)}")
            raise

    @classmethod
    async def get_user_messages(cls, user_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific user"""
        try:
            # Validate user ID
            if not user_id:
                raise ValueError("User ID cannot be empty")

            collection = await cls.get_messages_collection()
            cursor = collection.find({"user_id": user_id})
            messages = await cursor.to_list(length=None)
            
            # Convert datetime objects to ISO format strings
            for msg in messages:
                if isinstance(msg.get("timestamp"), datetime):
                    msg["timestamp"] = msg["timestamp"].isoformat()
                    
            logger.info(f"✅ Retrieved {len(messages)} messages for user {user_id}")
            return messages
        except Exception as e:
            logger.error(f"❌ Error getting user messages: {str(e)}")
            raise

    @classmethod
    async def delete_conversation(cls, conversation_id: str) -> bool:
        """Delete all messages in a conversation"""
        try:
            # Validate conversation ID
            if not conversation_id:
                raise ValueError("Conversation ID cannot be empty")

            collection = await cls.get_messages_collection()
            result = await collection.delete_many({"conversation_id": conversation_id})
            logger.info(f"✅ Deleted {result.deleted_count} messages from conversation {conversation_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"❌ Error deleting conversation: {str(e)}")
            raise 