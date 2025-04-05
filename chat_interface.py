import asyncio
import logging
import signal
from datetime import datetime
from config.database import Database
from services.summarizer import Summarizer

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_welcome_banner():
    """Print a welcome banner with instructions"""
    print("\n" + "="*50)
    print("🤖 Welcome to the Smart Chat Interface!")
    print("="*50)
    print("\nAvailable Commands:")
    print("  📝 'summary'  - Get an AI-powered summary of your conversation")
    print("  📜 'history'  - View your conversation history")
    print("  🚪 'exit'     - End the conversation")
    print("\nTips:")
    print("- Your messages are automatically saved and can be summarized anytime")
    print("- The AI will help identify key points in your conversation")
    print("- Use 'history' to review previous messages before getting a summary")
    print("="*50 + "\n")

async def cleanup():
    """Cleanup resources"""
    try:
        await Database.close_db()
        print("\n🔄 Closing database connection...")
        print("👋 Thank you for using the Smart Chat Interface!")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

async def main():
    """Main entry point for the chat interface"""
    try:
        # Initialize database connection
        print("🔄 Connecting to database...")
        await Database.connect_db()
        
        # Get user ID
        print("\n👤 Please identify yourself")
        user_id = input("Enter your user ID: ").strip()
        if not user_id:
            user_id = "default_user"
            print("ℹ️ Using default user ID: default_user")
        
        # Create new conversation
        conversation_id = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n✨ Starting new conversation")
        print(f"📌 Conversation ID: {conversation_id}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Initialize summarizer
        summarizer = Summarizer()
        
        # Show welcome message and instructions
        print_welcome_banner()
        
        while True:
            try:
                message = input("💬 Enter your message: ").strip()
                
                if message.lower() == 'exit':
                    print("\n👋 Goodbye! Thanks for chatting!")
                    break
                    
                elif message.lower() == 'summary':
                    try:
                        print("\n🤖 Generating conversation summary...")
                        summary = await summarizer.summarize_conversation(conversation_id)
                        print("\n" + "="*50)
                        print("📊 Conversation Summary")
                        print("="*50)
                        print(summary)
                        print("="*50 + "\n")
                    except Exception as e:
                        logger.error(f"Failed to generate summary: {str(e)}")
                        print("❌ Failed to generate summary. Please try again.")
                        
                elif message.lower() == 'history':
                    try:
                        messages = await Database.get_conversation(conversation_id)
                        print("\n" + "="*50)
                        print("📜 Conversation History")
                        print("="*50)
                        if not messages:
                            print("No messages in this conversation yet.")
                        else:
                            for msg in messages:
                                timestamp = datetime.fromisoformat(msg['timestamp']) if isinstance(msg['timestamp'], str) else msg['timestamp']
                                time_str = timestamp.strftime("%H:%M:%S")
                                print(f"[{time_str}] {msg['user_id']}: {msg['message']}")
                        print("="*50 + "\n")
                    except Exception as e:
                        logger.error(f"Failed to retrieve history: {str(e)}")
                        print("❌ Failed to retrieve conversation history. Please try again.")
                        
                else:
                    try:
                        message_data = {
                            "user_id": user_id,
                            "message": message,
                            "conversation_id": conversation_id,
                            "timestamp": datetime.now()
                        }
                        await Database.store_message(message_data)
                        print("✅ Message sent and stored successfully!")
                    except Exception as e:
                        logger.error(f"Failed to send message: {str(e)}")
                        print("❌ Failed to send message. Please try again.")
            except KeyboardInterrupt:
                print("\n\n🛑 Exiting chat...")
                break
            except Exception as e:
                logger.error(f"Error processing input: {str(e)}")
                print("❌ An error occurred. Please try again.")
    
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print("\n❌ An error occurred. Please check the logs for details.")
    finally:
        await cleanup()

def handle_sigterm(signum, frame):
    """Handle termination signals"""
    print("\n\n🛑 Received termination signal. Cleaning up...")
    asyncio.create_task(cleanup())

if __name__ == "__main__":
    try:
        # Set up signal handlers
        signal.signal(signal.SIGTERM, handle_sigterm)
        signal.signal(signal.SIGINT, handle_sigterm)
        
        # Run the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Chat interface terminated by user.")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print("\n❌ An error occurred. Please check the logs for details.")
    finally:
        try:
            loop.run_until_complete(cleanup())
            loop.close()
        except Exception:
            pass 