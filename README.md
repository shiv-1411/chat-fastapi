# Chat API with OpenAI Integration

A FastAPI-based chat application with OpenAI-powered conversation summarization.

## Features
- Create and manage chat messages
- Retrieve user-specific chat history
- OpenAI-powered chat summarization
- RESTful API endpoints
- In-memory storage for simplicity

## Prerequisites
- Python 3.11+
- OpenAI API key

## Local Setup

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
python main.py
```
The server will start at http://localhost:8080

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t chat-api .
```

2. Run the container:
```bash
docker run -d -p 8080:8080 -e OPENAI_API_KEY=your_api_key_here chat-api
```

## API Endpoints

### Create Chat Message
```bash
POST /api/v1/chats
{
    "user_id": "string",
    "message": "string"
}
```

### Get User Chat History
```bash
GET /api/v1/users/{user_id}/chats
```

### Get Specific Conversation
```bash
GET /api/v1/chats/{conversation_id}
```

### Delete Conversation
```bash
DELETE /api/v1/chats/{conversation_id}
```

## Cloud Deployment Options

### Heroku Deployment
1. Install Heroku CLI
2. Login to Heroku:
```bash
heroku login
```
3. Create a new Heroku app:
```bash
heroku create your-app-name
```
4. Set environment variables:
```bash
heroku config:set OPENAI_API_KEY=your_api_key_here
```
5. Deploy:
```bash
git push heroku main
```

### Railway/Render Deployment
1. Connect your GitHub repository to Railway/Render
2. Set the environment variables in the dashboard
3. Deploy from the main branch

## Development Notes
- The application uses in-memory storage for simplicity
- OpenAI API is used for chat summarization
- All endpoints return JSON responses
- Error handling is implemented for common scenarios

## Future Improvements
1. Add persistent storage
2. Implement user authentication
3. Add WebSocket support for real-time chat
4. Enhance summarization with more context
5. Add rate limiting

## Contributing
Feel free to open issues and pull requests for any improvements.

## License
MIT License 