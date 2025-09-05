import streamlit as st
import pandas as pd
from utils.snapshots import ensure_df_preview
from datetime import datetime

# Sample in-module dataset generation (also accessible via data/sample_datasets.csv)
def sample_climate_dataset():
    import numpy as np
    years = np.arange(2000, 2021)
    rainfall = 800 + (years - 2000) * 5 + np.random.normal(0, 30, len(years))
    df = pd.DataFrame({"year": years, "rainfall_mm": rainfall.round(2)})
    return df

def sample_medical_dataset():
    import numpy as np
    n = 200
    ages = np.random.randint(18, 80, n)
    systolic = 100 + 0.5 * ages + np.random.normal(0, 8, n)
    df = pd.DataFrame({"patient_id": [f"P{1000+i}" for i in range(n)], "age": ages, "systolic": systolic.round(0)})
    return df

class DataAgent:
    def __init__(self, ledger, snapshots):
        self.ledger = ledger
        self.snapshots = snapshots
        # core datasets
        self.datasets = {
            "climate_v1": {"df": sample_climate_dataset(), "privacy": "raw", "desc": "Climate rainfall (2000-2020)"},
            "med_stats_v1": {"df": sample_medical_dataset(), "privacy": "sensitive", "desc": "Patient vitals (synthetic)"}
        }
        # Role permissions (mock; replace with Descope-driven scopes)
        self.role_permissions = {
            "professor": {"access_raw": True, "access_anonymized": True, "access_aggregated": True},
            "student": {"access_raw": False, "access_anonymized": True, "access_aggregated": True},
            "external": {"access_raw": False, "access_anonymized": False, "access_aggregated": True}
        }

    def list_datasets(self):
        return [{"id": k, "desc": v["desc"], "privacy": v["privacy"]} for k, v in self.datasets.items()]

    def fetch_dataset(self, dataset_id, requester_role, access_level="auto"):
        if dataset_id not in self.datasets:
            raise ValueError("Dataset not found")
        df = self.datasets[dataset_id]["df"].copy()
        perms = self.role_permissions.get(requester_role, {})
        if access_level == "auto":
            if perms.get("access_raw"):
                mode = "raw"
            elif perms.get("access_anonymized"):
                mode = "anonymized"
            else:
                mode = "aggregated"
        else:
            mode = access_level

        if mode == "raw":
            return df, "raw"
        elif mode == "anonymized":
            df2 = df.copy()
            # drop id-like columns and add small noise to numeric columns
            to_drop = [c for c in df2.columns if "id" in c.lower() or "patient" in c.lower()]
            df2 = df2.drop(columns=to_drop, errors="ignore")
            for c in df2.select_dtypes(include="number").columns:
                df2[c] = (df2[c] + (df2[c].std() * 0.05 * pd.np.random.randn(len(df2)))).round(2)
            return df2, "anonymized"
        else:
            dfagg = df.select_dtypes(include="number").agg(["mean", "median", "std"]).T.reset_index()
            dfagg.columns = ["feature", "mean", "median", "std"]
            return dfagg, "aggregated"

    # Streamlit UI for dataset access
    def render_ui(self, user):
        st.subheader("Datasets")
        ds = self.list_datasets()
        for d in ds:
            with st.expander(f"{d['id']} — {d['desc']} (privacy: {d['privacy']})"):
                st.write(ensure_df_preview(self.datasets[d['id']]["df"]))
                if st.button(f"Request access to {d['id']}", key=f"req_{d['id']}"):
                    try:
                        df, mode = self.fetch_dataset(d['id'], user["role"])
                        sid = self.snapshots.save_snapshot(d['id'], df, {"mode": mode, "requested_by": user["email"], "created_at": datetime.utcnow().isoformat()})
                        self.ledger.log(user["email"], "fetch_dataset", {"dataset": d['id'], "mode": mode, "snapshot": sid})
                        st.success(f"Access granted ({mode}). Snapshot saved: {sid}")
                    except Exception as e:
                        st.error(str(e))
