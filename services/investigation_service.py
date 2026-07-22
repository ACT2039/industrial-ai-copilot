"""
Investigation Service
Handles SQLite persistence for the Enterprise Investigation Workspace.
"""
import sqlite3
import os
import time
import uuid
import json
from services.config_service import DATA_DIR

DB_PATH = os.path.join(DATA_DIR, "investigations.db")

def init_db():
    """Initializes the SQLite database schema."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Investigations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investigations (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at REAL,
            updated_at REAL,
            is_pinned INTEGER DEFAULT 0,
            is_archived INTEGER DEFAULT 0
        )
    ''')
    
    # Messages Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            investigation_id TEXT,
            timestamp REAL,
            query TEXT,
            query_intent TEXT,
            llm_answer TEXT,
            results_json TEXT,
            subgraph_json TEXT,
            metrics_json TEXT,
            coverage TEXT,
            coverage_reason TEXT,
            FOREIGN KEY(investigation_id) REFERENCES investigations(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys for cascade deletes
    conn.execute("PRAGMA foreign_keys = 1")
    return conn

def create_investigation(title="New Investigation"):
    inv_id = str(uuid.uuid4())
    now = time.time()
    conn = get_connection()
    conn.execute(
        "INSERT INTO investigations (id, title, created_at, updated_at, is_pinned, is_archived) VALUES (?, ?, ?, ?, ?, ?)",
        (inv_id, title, now, now, 0, 0)
    )
    conn.commit()
    conn.close()
    return inv_id

def get_investigations(include_archived=False):
    conn = get_connection()
    query = "SELECT * FROM investigations"
    if not include_archived:
        query += " WHERE is_archived = 0"
    query += " ORDER BY is_pinned DESC, updated_at DESC"
    cursor = conn.execute(query)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def search_investigations(search_query):
    conn = get_connection()
    search_term = f"%{search_query}%"
    
    # Search in titles and in messages
    query = """
        SELECT DISTINCT i.* FROM investigations i
        LEFT JOIN messages m ON i.id = m.investigation_id
        WHERE (i.title LIKE ? OR m.query LIKE ? OR m.llm_answer LIKE ?) 
        AND i.is_archived = 0
        ORDER BY i.is_pinned DESC, i.updated_at DESC
    """
    cursor = conn.execute(query, (search_term, search_term, search_term))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def update_investigation(inv_id, title=None, is_pinned=None, is_archived=None):
    conn = get_connection()
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if is_pinned is not None:
        updates.append("is_pinned = ?")
        params.append(1 if is_pinned else 0)
    if is_archived is not None:
        updates.append("is_archived = ?")
        params.append(1 if is_archived else 0)
        
    updates.append("updated_at = ?")
    params.append(time.time())
    
    params.append(inv_id)
    
    conn.execute(f"UPDATE investigations SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()

def delete_investigation(inv_id):
    conn = get_connection()
    conn.execute("DELETE FROM investigations WHERE id = ?", (inv_id,))
    conn.commit()
    conn.close()

def add_message(inv_id, query, intent, answer, results_json, subgraph_json, metrics_json, coverage, coverage_reason):
    msg_id = str(uuid.uuid4())
    now = time.time()
    conn = get_connection()
    
    conn.execute('''
        INSERT INTO messages 
        (id, investigation_id, timestamp, query, query_intent, llm_answer, results_json, subgraph_json, metrics_json, coverage, coverage_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (msg_id, inv_id, now, query, intent, answer, results_json, subgraph_json, metrics_json, coverage, coverage_reason))
    
    # Update investigation timestamp
    conn.execute("UPDATE investigations SET updated_at = ? WHERE id = ?", (now, inv_id))
    
    conn.commit()
    conn.close()
    return msg_id

def get_messages(inv_id):
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM messages WHERE investigation_id = ? ORDER BY timestamp ASC", (inv_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
