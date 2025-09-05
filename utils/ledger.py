import datetime
import requests
import os

# ⚠️ Replace with your Azure Confidential Ledger details
ACL_ENDPOINT = os.getenv("ACL_ENDPOINT", "https://your-ledger-name.confidential-ledger.azure.com")
ACL_API_VERSION = "2022-05-13"
ACL_API_KEY = os.getenv("ACL_API_KEY", "your-acl-api-key")

class Ledger:
    """Audit logging via Azure Confidential Ledger (fallback to local logs)."""

    def __init__(self):
        self.local_log = []

    def log(self, actor, action, resource, status="SUCCESS"):
        entry = {
            "actor": actor,
            "action": action,
            "resource": resource,
            "status": status,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        # Try pushing to ACL
        try:
            headers = {
                "Content-Type": "application/json",
                "x-ms-date": datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "x-ms-version": ACL_API_VERSION,
                "Ocp-Apim-Subscription-Key": ACL_API_KEY
            }
            resp = requests.post(f"{ACL_ENDPOINT}/app/logs?api-version={ACL_API_VERSION}", json=entry, headers=headers)
            if resp.status_code == 200:
                return entry
        except:
            pass

        self.local_log.append(entry)
        return entry

    def get_logs(self):
        """Retrieve logs from ACL or fallback to local log."""
        try:
            headers = {"Ocp-Apim-Subscription-Key": ACL_API_KEY}
            resp = requests.get(f"{ACL_ENDPOINT}/app/logs?api-version={ACL_API_VERSION}", headers=headers)
            if resp.status_code == 200:
                return resp.json().get("value", [])
        except:
            pass
        return self.local_log
