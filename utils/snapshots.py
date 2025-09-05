import datetime

class SnapshotManager:
    """Manages versioned research snapshots."""

    def __init__(self):
        self.snapshots = []

    def create_snapshot(self, dataset, analysis_result, user):
        snapshot = {
            "id": len(self.snapshots) + 1,
            "dataset": dataset,
            "result": analysis_result,
            "user": user,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        self.snapshots.append(snapshot)
        return snapshot

    def list_snapshots(self):
        return self.snapshots
