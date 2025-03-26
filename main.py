from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import chat_routes

app = FastAPI(title="Chat API")

# Include chat routes
app.include_router(chat_routes.router, tags=["chats"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Chat API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
