import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any

class HistoryManager:
    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Creates the necessary tables if they don't exist."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Table for Chat Sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                preview TEXT
            )
        """)

        # Table for Messages within a Session
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
            )
        """)
        
        conn.commit()
        conn.close()


    def save_session(self, user_id: str, messages: List[Any]) -> str:
        """
        Saves a full chat session and its messages.
        Returns the session_id.
        """
        if not messages:
            return None

        conn = self._get_conn()
        cursor = conn.cursor()

        # Generate a unique session ID
        session_id = f"{user_id}_{int(datetime.now().timestamp())}"
        
        # Create a preview from the first user message or just the first message
        preview = "Empty chat"
        for m in messages:
            # Handle LangChain message objects or dicts
            content = m.content if hasattr(m, "content") else m.get("content", "")
            type_ = m.type if hasattr(m, "type") else m.get("type", "unknown")
            
            if type_ == "human":
                preview = content[:50] + "..." if len(content) > 50 else content
                break
        else:
             # Fallback if no human message found
             first_msg = messages[0]
             content = first_msg.content if hasattr(first_msg, "content") else first_msg.get("content", "")
             preview = content[:50] + "..." if len(content) > 50 else content

        # Insert Session
        cursor.execute(
            "INSERT INTO sessions (session_id, user_id, preview) VALUES (?, ?, ?)",
            (session_id, user_id, preview)
        )

        # Insert Messages
        for m in messages:
            content = m.content if hasattr(m, "content") else m.get("content", "")
            type_ = m.type if hasattr(m, "type") else m.get("type", "unknown")
            
            cursor.execute(
                "INSERT INTO messages (session_id, type, content) VALUES (?, ?, ?)",
                (session_id, type_, content)
            )

        conn.commit()
        conn.close()
        return session_id

    def get_recent_sessions(self, user_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Returns the latest 'limit' sessions for a user.
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT session_id, timestamp, preview 
            FROM sessions 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()

        sessions = []
        for r in rows:
            sessions.append({
                "session_id": r[0],
                "timestamp": r[1],
                "preview": r[2]
            })
        
        return sessions

    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all messages for a specific session.
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT type, content, timestamp 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY id ASC
        """, (session_id,))
        
        rows = cursor.fetchall()
        conn.close()

        messages = []
        for r in rows:
            messages.append({
                "type": r[0],
                "content": r[1],
                "timestamp": r[2]
            })
            
        return messages

    def delete_session(self, session_id: str):
        """
        Deletes a session and its messages.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        
        conn.commit()
        conn.close()
