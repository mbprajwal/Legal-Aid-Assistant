import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from src.history_manager import HistoryManager

# Initialize FastAPI app
app = FastAPI(title="Mock Legal Aid API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize History Manager
history_manager = HistoryManager()

# Mock Session Storage (In-Memory for active chat)
active_sessions: Dict[str, List[Dict[str, str]]] = {}

class ChatRequest(BaseModel):
    user_query: str
    user_id: str = "default_user"

class SaveChatRequest(BaseModel):
    user_id: str = "default_user"
    session_id: Optional[str] = None

class ResetRequest(BaseModel):
    user_id: str = "default_user"

@app.get("/")
def read_root():
    return {"message": "Mock Legal Aid API is running"}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    user_id = request.user_id
    query = request.user_query
    
    # Initialize session if not exists
    if user_id not in active_sessions:
        active_sessions[user_id] = []
    
    # Store user message
    active_sessions[user_id].append({"role": "user", "content": query})
    
    # Generate mock response
    response_text = f"This is a mock response to: '{query}'. The backend is running in lightweight mode."
    
    # Store bot response
    active_sessions[user_id].append({"role": "assistant", "content": response_text})
    
    return {"response": response_text}

@app.post("/chat/save")
def save_chat(request: SaveChatRequest):
    user_id = request.user_id
    messages = active_sessions.get(user_id, [])
    
    if not messages:
        return {"status": "ignored", "message": "No messages to save"}
    
    # Convert dict messages to object-like structure expected by HistoryManager if needed,
    # or update HistoryManager to handle dicts. 
    # Looking at HistoryManager code, it handles objects with .content/.type OR dicts with .get().
    # Our messages are dicts with "role" and "content". 
    # HistoryManager expects "type" (human/ai) and "content".
    
    formatted_messages = []
    for m in messages:
        formatted_messages.append({
            "type": "human" if m["role"] == "user" else "ai",
            "content": m["content"]
        })
        
    new_session_id = history_manager.save_session(user_id, formatted_messages)
    
    # If an old session_id was provided, delete it to avoid duplicates
    if request.session_id:
        history_manager.delete_session(request.session_id)
        
    return {"status": "saved", "session_id": new_session_id}

@app.get("/chat/history")
def get_history(user_id: str = "default_user"):
    sessions = history_manager.get_recent_sessions(user_id, limit=10)
    return {"sessions": sessions}

@app.get("/chat/session/{session_id}")
def get_session_history(session_id: str):
    messages = history_manager.get_session_messages(session_id)
    # Convert back to role/content format for frontend
    formatted_messages = []
    for m in messages:
        role = "user" if m["type"] == "human" else "assistant"
        formatted_messages.append({"role": role, "content": m["content"]})
    return {"messages": formatted_messages}

@app.post("/chat/new")
def new_chat(request: ResetRequest):
    user_id = request.user_id
    if user_id in active_sessions:
        active_sessions[user_id] = []
    return {"status": "success", "message": "New chat started, memory cleared"}

class RestoreRequest(BaseModel):
    user_id: str
    messages: List[Dict[str, str]]

@app.post("/chat/restore")
def restore_chat(request: RestoreRequest):
    user_id = request.user_id
    active_sessions[user_id] = request.messages
    return {"status": "success", "message": "Chat history restored to memory"}

@app.get("/templates")
def get_templates():
    return {"templates": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
