import pandas as pd
import uuid
from datetime import datetime
import os

class SnapshotManager:
    def __init__(self, ledger=None):
        self.ledger = ledger
        self.snapshots = {}  # id => {"dataset_id", "df", "metadata"}
        # Create sample data directory if needed
        self._ensure_sample_data()

    def _ensure_sample_data(self):
        # no-op for demo; users may replace with real CSV paths
        pass

    def save_snapshot(self, dataset_id, df, metadata=None):
        sid = str(uuid.uuid4())
        self.snapshots[sid] = {"id": sid, "dataset_id": dataset_id, "df": df.copy(), "metadata": metadata or {}, "created_at": datetime.utcnow().isoformat()}
        if self.ledger:
            self.ledger.log("SnapshotManager", "save_snapshot", {"id": sid, "dataset_id": dataset_id, "metadata": metadata})
        return sid

    def get_snapshot(self, sid):
        return self.snapshots.get(sid)

    def list_snapshots(self):
        return list(self.snapshots.values())

    # Helper to produce simple anonymized df for governance demo
    def get_dataset_anon(self, dataset_id):
        # If dataset present in snapshot store return anonymized view; fallback to simple generator
        # Search last saved raw snapshot for dataset
        for s in reversed(self.snapshots.values()):
            if s["dataset_id"] == dataset_id:
                df = s["df"].copy()
                # drop id-like columns and add small noise
                df2 = df.copy()
                to_drop = [c for c in df2.columns if "id" in c.lower() or "patient" in c.lower()]
                df2 = df2.drop(columns=to_drop, errors="ignore")
                for c in df2.select_dtypes(include="number").columns:
                    df2[c] = (df2[c] + (df2[c].std() * 0.05 * pd.np.random.randn(len(df2)))).round(2)
                return df2
        # fallback sample
        return self.get_dataset_sample(dataset_id)

    def get_dataset_sample(self, dataset_id):
        # small sample generator
        if dataset_id.startswith("climate"):
            import numpy as np
            years = np.arange(2000, 2021)
            rainfall = 800 + (years - 2000) * 5 + np.random.normal(0, 30, len(years))
            return pd.DataFrame({"year": years, "rainfall_mm": rainfall.round(2)})
        else:
            import numpy as np
            n = 50
            ages = np.random.randint(18, 80, n)
            systolic = 100 + 0.5 * ages + np.random.normal(0, 8, n)
            return pd.DataFrame({"patient_id": [f"P{1000+i}" for i in range(n)], "age": ages, "systolic": systolic.round(0)})

    def df_from_object(self, obj):
        return pd.DataFrame(obj)

# utility for small preview
def ensure_df_preview(df):
    try:
        return df.head(10)
    except Exception:
        return str(df)
