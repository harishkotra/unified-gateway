import sqlite3
import time
from typing import Optional
from datetime import datetime

class RequestLogger:
    def __init__(self, db_path="requests.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                model_requested TEXT,
                model_used TEXT,
                provider TEXT,
                latency_ms REAL,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                status_code INTEGER,
                fallback_used BOOLEAN,
                error_message TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def log_request(self, 
                    model_requested: str,
                    model_used: str,
                    provider: str,
                    latency_ms: float,
                    usage: dict,
                    status_code: int,
                    fallback_used: bool = False,
                    error_message: Optional[str] = None):
        
        timestamp = datetime.now().isoformat()
        prompt_tokens = usage.get("prompt_tokens", 0) if usage else 0
        completion_tokens = usage.get("completion_tokens", 0) if usage else 0
        total_tokens = usage.get("total_tokens", 0) if usage else 0

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO request_logs (
                    timestamp, model_requested, model_used, provider, latency_ms,
                    prompt_tokens, completion_tokens, total_tokens, status_code,
                    fallback_used, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, model_requested, model_used, provider, latency_ms,
                prompt_tokens, completion_tokens, total_tokens, status_code,
                fallback_used, error_message
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to log request: {e}")

# Global logger instance
request_logger = RequestLogger()
