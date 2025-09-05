# utils/ledger.py
import sqlite3
import hashlib
import time

class AuditLedger:
    """
    Lightweight immutable ledger using SQLite + hash chaining.
    Replaces Azure Confidential Ledger for hackathon/demo use.
    """

    def __init__(self, db_path="researchmesh_ledger.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        cur = self.conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                actor TEXT,
                action TEXT,
                resource TEXT,
                prev_hash TEXT,
                hash TEXT
            )"""
        )
        self.conn.commit()

    def log(self, actor, action, resource):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cur = self.conn.cursor()

        # Get last hash
        cur.execute("SELECT hash FROM logs ORDER BY id DESC LIMIT 1")
        prev_hash = cur.fetchone()
        prev_hash = prev_hash[0] if prev_hash else "0"

        # Create new hash (link to previous log)
        data = f"{timestamp}{actor}{action}{resource}{prev_hash}".encode()
        entry_hash = hashlib.sha256(data).hexdigest()

        cur.execute(
            "INSERT INTO logs (timestamp, actor, action, resource, prev_hash, hash) VALUES (?,?,?,?,?,?)",
            (timestamp, actor, action, resource, prev_hash, entry_hash),
        )
        self.conn.commit()

    def get_logs(self):
        cur = self.conn.cursor()
        cur.execute("SELECT timestamp, actor, action, resource, hash FROM logs")
        return cur.fetchall()

    def verify_chain(self):
        """
        Verify integrity of the entire ledger.
        Returns True if valid, False if tampered.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT timestamp, actor, action, resource, prev_hash, hash FROM logs ORDER BY id")
        rows = cur.fetchall()

        prev_hash = "0"
        for (timestamp, actor, action, resource, prev_h, entry_hash) in rows:
            # recompute hash
            data = f"{timestamp}{actor}{action}{resource}{prev_hash}".encode()
            expected_hash = hashlib.sha256(data).hexdigest()
            if entry_hash != expected_hash:
                return False
            prev_hash = entry_hash
        return True
