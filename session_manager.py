from typing import Dict, Any, List
import time
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "honeypot_sessions.db")

class SessionManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        # Enable dictionary-like access to rows
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    sessionId TEXT PRIMARY KEY,
                    confidence REAL,
                    agent_active INTEGER,
                    total_messages INTEGER,
                    intelligence TEXT,
                    callback_sent INTEGER,
                    chat_history TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            """)
            conn.commit()

    def _row_to_dict(self, row) -> Dict[str, Any]:
        if not row:
            return None
        return {
            "sessionId": row["sessionId"],
            "confidence": row["confidence"],
            "agent_active": bool(row["agent_active"]),
            "total_messages": row["total_messages"],
            "intelligence": json.loads(row["intelligence"]),
            "callback_sent": bool(row["callback_sent"]),
            "chat_history": json.loads(row["chat_history"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def create_session(self, session_id: str) -> Dict[str, Any]:
        default_intelligence = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }
        default_chat_history = []
        now = time.time()
        
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO sessions 
                (sessionId, confidence, agent_active, total_messages, intelligence, callback_sent, chat_history, created_at, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, 0.0, 0, 0, 
                json.dumps(default_intelligence), 0, json.dumps(default_chat_history),
                now, now
            ))
            conn.commit()
            
        return self.get_session(session_id)

    def get_session(self, session_id: str) -> Dict[str, Any]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE sessionId = ?", (session_id,)).fetchone()
            if row is None:
                return self.create_session(session_id)
            return self._row_to_dict(row)
            
    def _update_field(self, session_id: str, field: str, value: Any):
        now = time.time()
        with self._get_conn() as conn:
            conn.execute(f"UPDATE sessions SET {field} = ?, updated_at = ? WHERE sessionId = ?", (value, now, session_id))
            conn.commit()

    def update_confidence(self, session_id: str, delta: float):
        session = self.get_session(session_id)
        new_conf = min(1.0, session["confidence"] + delta)
        self._update_field(session_id, "confidence", new_conf)

    def activate_agent(self, session_id: str):
        self._update_field(session_id, "agent_active", 1)

    def increment_message_count(self, session_id: str):
        session = self.get_session(session_id)
        self._update_field(session_id, "total_messages", session["total_messages"] + 1)

    def add_intelligence(self, session_id: str, key: str, values: list):
        session = self.get_session(session_id)
        existing = set(session["intelligence"].get(key, []))
        added = False
        for v in values:
            if v not in existing:
                session["intelligence"][key].append(v)
                added = True
        if added:
            self._update_field(session_id, "intelligence", json.dumps(session["intelligence"]))

    def mark_callback_sent(self, session_id: str):
        self._update_field(session_id, "callback_sent", 1)
        
    def save_chat_history(self, session_id: str, history: List[Dict[str, str]]):
        self._update_field(session_id, "chat_history", json.dumps(history))

    def cleanup_stale(
        self,
        max_idle_seconds: float = 86400,
        exclude_session_id: str | None = None,
    ) -> list[str]:
        now = time.time()
        cutoff = now - max_idle_seconds
        
        with self._get_conn() as conn:
            if exclude_session_id:
                cursor = conn.execute("SELECT sessionId FROM sessions WHERE updated_at < ? AND sessionId != ?", (cutoff, exclude_session_id))
            else:
                cursor = conn.execute("SELECT sessionId FROM sessions WHERE updated_at < ?", (cutoff,))
                
            to_remove = [row["sessionId"] for row in cursor.fetchall()]
            
            if to_remove:
                placeholders = ",".join("?" * len(to_remove))
                conn.execute(f"DELETE FROM sessions WHERE sessionId IN ({placeholders})", tuple(to_remove))
                conn.commit()
                
        return to_remove
