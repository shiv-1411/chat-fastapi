import os
import openai
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

class SummarizationService:
    def __init__(self):
        """Initialize OpenAI client"""
        openai.api_key = os.getenv("OPENAI_API_KEY")

    async def generate_summary(self, messages):
        """Generate a summary of the chat messages using OpenAI"""
        if not messages:
            return "No messages to summarize"

        # Format messages for the prompt
        formatted_messages = "\n".join([
            f"{msg['user_id']}: {msg['message']}"
            for msg in messages
        ])

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
                    {"role": "user", "content": f"Please summarize this conversation:\n{formatted_messages}"}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return "Error generating summary"

    async def generate_summary_old(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of the chat conversation using OpenAI's GPT model.
        
        Args:
            messages: List of chat messages to summarize
        
        Returns:
            Dict containing summary, key points, and sentiment
        """
        try:
            # Format messages for the prompt
            formatted_chat = "\n".join([
                f"{msg['user_id']}: {msg['message']}"
                for msg in messages
            ])

            # Create the prompt for summarization
            prompt = f"""Please analyze the following chat conversation and provide:
1. A brief summary (2-3 sentences)
2. Key points discussed
3. Overall sentiment
4. Action items (if any)

Conversation:
{formatted_chat}"""

            # Use the older version's API format
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return {
                "summary": response['choices'][0]['message']['content'],
                "message_count": len(messages),
                "status": "success"
            }
            
        except openai.error.RateLimitError:
            return {
                "error": "Rate limit exceeded. Please try again later.",
                "status": "error"
            }
        except openai.error.AuthenticationError:
            return {
                "error": "Invalid API key. Please check your OpenAI API key.",
                "status": "error"
            }
        except Exception as e:
            return {
                "error": f"An error occurred: {str(e)}",
                "status": "error"
            } 