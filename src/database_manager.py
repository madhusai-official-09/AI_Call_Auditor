import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="database/audits.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Create table for audits
        c.execute('''
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                file_name TEXT,
                audit_type TEXT, -- 'audio' or 'chat'
                score INTEGER,
                violations TEXT, -- JSON string
                summary TEXT,
                status TEXT -- 'Processed', 'Flagged'
            )
        ''')
        conn.commit()
        conn.close()

    def log_audit(self, file_name, audit_type, audit_result):
        """
        Logs an audit result to SQLite. Overwrites if file_name exists.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if file already exists, if so delete it to ensure fresh audit
        c.execute("DELETE FROM audits WHERE file_name = ?", (file_name,))
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        score = audit_result.get("score", 0)
        violations = json.dumps(audit_result.get("violations", []))
        summary = audit_result.get("summary", "")
        # Flag if score is low or violations exist
        status = "Flagged" if score < 70 or audit_result.get("violations") else "Solved"

        c.execute('''
            INSERT INTO audits (timestamp, file_name, audit_type, score, violations, summary, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, file_name, audit_type, score, violations, summary, status))
        
        conn.commit()
        conn.close()
        return status

    def get_all_audits(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM audits ORDER BY id DESC")
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows
        
    def clear_all_data(self):
        """
        Wipes all data from the database.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM audits")
        conn.commit()
        conn.close()
