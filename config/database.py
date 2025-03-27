# In-memory storage
chat_messages = []
conversation_counter = 0

def get_next_conversation_id():
    global conversation_counter
    conversation_counter += 1
    return f"conv_{conversation_counter}"

def get_next_message_id():
    return f"msg_{len(chat_messages) + 1}" 