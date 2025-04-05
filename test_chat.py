import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8080/api/v1"

def test_chat_system():
    print("\n=== Testing Chat System with MongoDB ===\n")
    
    # 1. Create first message
    print("1. Creating first message...")
    message1 = {
        "user_id": "user1",
        "message": "Hello! How are you?"
    }
    response = requests.post(f"{BASE_URL}/chats", json=message1)
    print(f"Response: {response.json()}")
    conversation_id = response.json()["conversation_id"]
    
    # 2. Create second message in same conversation
    print("\n2. Creating second message in same conversation...")
    message2 = {
        "user_id": "user2",
        "message": "I'm doing great! How about you?",
        "conversation_id": conversation_id
    }
    response = requests.post(f"{BASE_URL}/chats", json=message2)
    print(f"Response: {response.json()}")
    
    # 3. Get conversation
    print("\n3. Getting conversation...")
    response = requests.get(f"{BASE_URL}/chats/{conversation_id}")
    print(f"Conversation: {json.dumps(response.json(), indent=2)}")
    
    # 4. Get user1's chat history
    print("\n4. Getting user1's chat history...")
    response = requests.get(f"{BASE_URL}/users/user1/chats")
    print(f"User1's messages: {json.dumps(response.json(), indent=2)}")
    
    # 5. Get user2's chat history
    print("\n5. Getting user2's chat history...")
    response = requests.get(f"{BASE_URL}/users/user2/chats")
    print(f"User2's messages: {json.dumps(response.json(), indent=2)}")
    
    # 6. Delete conversation
    print("\n6. Deleting conversation...")
    response = requests.delete(f"{BASE_URL}/chats/{conversation_id}")
    print(f"Delete response: {response.json()}")
    
    # 7. Verify conversation is deleted
    print("\n7. Verifying conversation is deleted...")
    response = requests.get(f"{BASE_URL}/chats/{conversation_id}")
    print(f"Response status: {response.status_code}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_chat_system() 