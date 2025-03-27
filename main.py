from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat_routes
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Chat API",
    description="REST API for managing chat messages",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include chat routes
app.include_router(
    chat_routes.router,
    prefix="/api/v1",  # Adding version prefix
    tags=["chats"]
)

@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "Chat API is running",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": {
            "store_chat": "POST /api/v1/chats",
            "get_conversation": "GET /api/v1/chats/{conversation_id}",
            "get_user_chats": "GET /api/v1/users/{user_id}/chats",
            "delete_conversation": "DELETE /api/v1/chats/{conversation_id}"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True  # Enable auto-reload during development
    )
