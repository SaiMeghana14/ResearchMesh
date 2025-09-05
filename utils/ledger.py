import sqlite3
import uuid
import json
from datetime import datetime
import pandas as pd

class AuditLedger:
    def __init__(self, db_path="researchmesh_ledger.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_table()

    def _init_table(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS ledger (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                actor TEXT,
                action TEXT,
                details TEXT
            )
        """)
        self.conn.commit()

    def log(self, actor, action, details: dict):
        c = self.conn.cursor()
        entry_id = str(uuid.uuid4())
        c.execute("INSERT INTO ledger VALUES (?,?,?,?,?)", (entry_id, datetime.utcnow().isoformat(), actor, action, json.dumps(details)))
        self.conn.commit()
        return entry_id

    def recent(self, limit=50):
        c = self.conn.cursor()
        rows = c.execute("SELECT id,timestamp,actor,action,details FROM ledger ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
        df = pd.DataFrame(rows, columns=["id", "timestamp", "actor", "action", "details"])
        return df
