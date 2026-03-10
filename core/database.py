import sqlite3
import json
import os

class MemoryDB:
    def __init__(self, db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'zh',
                msg_cnt INTEGER DEFAULT 0,
                messages TEXT DEFAULT '[]',
                log_buffer TEXT DEFAULT '[]',
                daily_summary TEXT DEFAULT '[]',
                mega_summary TEXT DEFAULT '[]'
            )
        ''')
        
        self.conn.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS micro_memory USING fts5(
                user_id UNINDEXED,
                date UNINDEXED,
                source_type UNINDEXED,
                content,
                tags
            )
        ''')
        self.conn.commit()

    def insert_micro_memory(self, user_id, date, source_type, content, tags=""):
        self.conn.execute(
            "INSERT INTO micro_memory (user_id, date, source_type, content, tags) VALUES (?, ?, ?, ?, ?)",
            (user_id, date, source_type, content, tags)
        )
        self.conn.commit()

    def search_memory(self, user_id, query_text, limit=3):
        cur = self.conn.execute('''
            SELECT date, source_type, content 
            FROM micro_memory 
            WHERE user_id = ? AND micro_memory MATCH ? 
            ORDER BY rank 
            LIMIT ?
        ''', (user_id, query_text, limit))
        
        results = cur.fetchall()
        if not results:
            return ""
            
        formatted_docs = "\n### Retrieved Precise Memory:\n"
        for row in results:
            formatted_docs += f"[{row['date']} | {row['source_type']}]: {row['content']}\n"
        return formatted_docs
    