from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
import pyrebase
import json
from pydantic import BaseModel
import uvicorn

API_URL = "http://127.0.0.1:8000"

import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your chains
from src.combined_chain import CombinedLegalChatbot     
from src.document_chain import DocumentGeneratorChain
from src.history_manager import HistoryManager

app = FastAPI(title="Legal Aid Assistant API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount generated documents directory
os.makedirs("generated_documents", exist_ok=True)
app.mount("/generated_documents", StaticFiles(directory="generated_documents"), name="generated_documents")

# Global State
# active_sessions = { "user_id": CombinedLegalChatbot_instance }
active_sessions = {}
history_manager = HistoryManager()
doc_chain = DocumentGeneratorChain()

def get_session(user_id: str):
    """Get or create a chatbot session for a specific user."""
    if user_id not in active_sessions:
        print(f"✨ Creating new session for user: {user_id}")
        active_sessions[user_id] = CombinedLegalChatbot()
    return active_sessions[user_id]

# ----------- MODELS -----------
class ChatRequest(BaseModel):
    user_query: str
    user_id: str = "default_user"  # Added user_id

from typing import Optional

class SaveChatRequest(BaseModel):
    user_id: str = "default_user"
    session_id: Optional[str] = None  # Added session_id

class ResetRequest(BaseModel):
    user_id: str = "default_user"

class RestoreRequest(BaseModel):
    user_id: str
    messages: list

class DocumentRequest(BaseModel):
    template_name: str
    user_inputs: dict
    user_query: str

# ----------- ENDPOINTS -----------

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    chatbot = get_session(request.user_id)
    response = chatbot.generate(request.user_query)
    return {"response": response}

@app.post("/chat/save")
def save_chat(request: SaveChatRequest):
    """Saves the current chat session to SQLite database."""
    print(f"DEBUG: Saving chat for user {request.user_id}, session {request.session_id}")
    chatbot = get_session(request.user_id)
    
    # Debug: Print memory type and contents
    print(f"DEBUG: Chatbot memory type: {type(chatbot.memory)}")
    try:
        messages = chatbot.memory.get_history()
        print(f"DEBUG: Retrieved messages count: {len(messages) if messages else 0}")
        if messages:
            print(f"DEBUG: First message: {messages[0]}")
    except Exception as e:
        print(f"DEBUG: Error getting history: {e}")
        messages = []
    
    if not messages:
        print("DEBUG: No messages to save")
        return {"status": "ignored", "message": "No messages to save"}
    
    session_id = history_manager.save_session(request.user_id, messages)
    print(f"DEBUG: Saved session {session_id}")
    
    # If an old session_id was provided, delete it to avoid duplicates
    if request.session_id:
        print(f"DEBUG: Deleting old session {request.session_id}")
        history_manager.delete_session(request.session_id)
        
    return {"status": "saved", "session_id": session_id}

@app.post("/chat/restore")
def restore_chat(request: RestoreRequest):
    """Restores chat history into the chatbot's memory."""
    chatbot = get_session(request.user_id)
    
    # Clear existing memory first
    chatbot.memory.history.clear()
    
    # Restore messages
    for msg in request.messages:
        if msg.get("role") == "user":
            chatbot.memory.add_user_message(msg.get("content"))
        elif msg.get("role") == "assistant":
            chatbot.memory.add_assistant_response(msg.get("content"))
            
    return {"status": "success", "message": "Chat history restored"}

@app.get("/chat/session/{session_id}")
def get_session_history(session_id: str):
    messages = history_manager.get_session_messages(session_id)
    # Convert back to role/content format for frontend
    formatted_messages = []
    for m in messages:
        role = "user" if m["type"] == "human" else "assistant"
        formatted_messages.append({"role": role, "content": m["content"]})
    return {"messages": formatted_messages}

@app.post("/document/generate")
def generate_document(request: DocumentRequest):
    pdf_path, text = doc_chain.generate(
        template_name=request.template_name,
        field_values=request.user_inputs,
        user_query=request.user_query
    )
    
    # Convert absolute path to relative URL path
    filename = os.path.basename(pdf_path)
    try:
        rel_path = os.path.relpath(pdf_path, os.getcwd())
    except ValueError:
        rel_path = pdf_path

    rel_path = rel_path.replace("\\", "/")
    
    if rel_path.startswith("generated_documents/"):
        url_path = rel_path
    else:
        url_path = f"generated_documents/{os.path.basename(pdf_path)}"

    download_url = f"{API_URL}/{url_path}"

    return {
        "message": "Document generated successfully",
        "pdf_url": download_url,
        "content_preview": text[:500]
    }

@app.get("/templates")
def list_templates():
    template_dir = "src/templates"
    templates = []
    if os.path.exists(template_dir):
        for filename in os.listdir(template_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(template_dir, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        templates.append({
                            "id": filename.replace(".json", ""),
                            "title": data.get("title", filename),
                            "fields": data.get("fields", {})
                        })
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
    return {"templates": templates}

@app.get("/chat/history")
def get_history(user_id: str = "default_user"):
    """Retrieves the last 3 chat sessions from SQLite."""
    sessions = history_manager.get_recent_sessions(user_id, limit=3)
    return {"sessions": sessions}

@app.post("/chat/new")
def new_chat(request: ResetRequest):
    """Clears the current memory to start a fresh chat."""
    chatbot = get_session(request.user_id)
    
    # Clear the in-memory history
    chatbot.memory.history.clear()
    # Reset any active document state
    chatbot._clear_document_state()
    return {"status": "success", "message": "New chat started, memory cleared"}

@app.post("/session/reset")
def reset_memory(request: ResetRequest):
    chatbot = get_session(request.user_id)
    chatbot.memory.history.clear()
    return {"status": "Memory cleared"}


# ----------- AUTHENTICATION -----------

firebaseConfig = {
    "apiKey": "AIzaSyCqREwfAsApRLrdgHSeA1q09pfVt0vOLPs",
    "authDomain": "legal-aid-ead1c.firebaseapp.com",
    "databaseURL": "https://legal-aid-ead1c-default-rtdb.firebaseio.com",
    "projectId": "legal-aid-ead1c",
    "storageBucket": "legal-aid-ead1c.appspot.com",
    "messagingSenderId": "888124238174",
    "appId": "1:888124238174:web:5da2372465b7c1430ec7cf",
    "measurementId": "G-GEW1E0F7F1"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

USERS_FILE = "users.json"

def save_user_to_file(user_data):
    users = []
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        except:
            pass
    
    # Check if user already exists and update, or append
    for i, u in enumerate(users):
        if u.get("email") == user_data["email"]:
            users[i] = user_data
            break
    else:
        users.append(user_data)
        
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def get_user_from_file(email):
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
                for user in users:
                    if user.get("email") == email:
                        return user
        except:
            pass
    return None

class User(BaseModel):
    email: str
    password: str

class SignupUser(User):
    firstName: str
    lastName: str

@app.post("/signup")
def signup(user: SignupUser):
    try:
        auth.create_user_with_email_and_password(user.email, user.password)
        # Save additional details to local file
        save_user_to_file(user.dict())
        return {"message": "Signup successful"}
    except Exception as e:
        error_message = str(e)
        try:
            if "{" in error_message:
                json_part = error_message[error_message.find("{"):]
                error_data = json.loads(json_part)
                if "error" in error_data and "message" in error_data["error"]:
                    error_message = error_data["error"]["message"]
        except:
            pass
        raise HTTPException(status_code=400, detail=error_message)


@app.post("/login")
def login(user: User):
    try:
        auth.sign_in_with_email_and_password(user.email, user.password)
        # Fetch user details
        user_data = get_user_from_file(user.email)
        response = {"message": "Login successful"}
        if user_data:
            response["firstName"] = user_data.get("firstName", "")
            response["lastName"] = user_data.get("lastName", "")
        else:
            # Fallback if not found in local file
            response["firstName"] = "User"
            response["lastName"] = ""
            
        return response
    except Exception as e:
        error_message = str(e)
        try:
            if "{" in error_message:
                json_part = error_message[error_message.find("{"):]
                error_data = json.loads(json_part)
                if "error" in error_data and "message" in error_data["error"]:
                    error_message = error_data["error"]["message"]
        except:
            pass
        raise HTTPException(status_code=400, detail=error_message)


if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000)
