from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from config.database import Database
from routes import chat_routes, summary_routes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chat API",
    description="A simple chat API with MongoDB storage and GPT-3.5 summarization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_routes.router, prefix="/api/v1", tags=["chats"])
app.include_router(summary_routes.router, prefix="/api/v1", tags=["summaries"])

@app.on_event("startup")
async def startup_event():
    try:
        await Database.connect_db()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    try:
        await Database.close_db()
        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Chat API",
        "version": "1.0.0",
        "status": "running",
        "features": ["chat", "summarization"]
    }
