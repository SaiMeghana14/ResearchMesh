import streamlit as st
import pandas as pd
import time
import json
from sklearn.linear_model import LinearRegression
from datetime import datetime

class AnalysisAgent:
    def __init__(self, ledger, snapshots):
        self.ledger = ledger
        self.snapshots = snapshots

    def run_analysis(self, dataset_id, df, params=None):
        self.ledger.log("AnalysisAgent", "analysis_start", {"dataset": dataset_id, "params": params})
        time.sleep(0.6)
        result = {}
        if dataset_id.startswith("climate"):
            # Forecast next 5 years rainfall with linear regression on year -> rainfall
            X = df[["year"]].values
            y = df["rainfall_mm"].values
            model = LinearRegression().fit(X, y)
            future = list(range(int(df["year"].max()) + 1, int(df["year"].max()) + 6))
            preds = model.predict([[yr] for yr in future]).round(2).tolist()
            result = {"type": "timeseries_forecast", "x": future, "y": preds, "summary": f"Predicted rainfall (next 5 years): {preds}"}
        else:
            stats = df.select_dtypes(include="number").agg(["mean", "median"]).T.round(2).reset_index().to_dict(orient="records")
            result = {"type": "aggregate_stats", "stats": stats, "summary": "Aggregated numeric statistics computed."}
        self.ledger.log("AnalysisAgent", "analysis_end", {"dataset": dataset_id, "summary": result.get("summary", "")})
        # Save result as a snapshot
        sid = self.snapshots.save_snapshot(dataset_id, pd.DataFrame({"result": [json.dumps(result)]}), {"type": "analysis_result", "created_at": datetime.utcnow().isoformat()})
        return result, sid

    def render_ui(self, user):
        st.subheader("Run Analysis")
        snaps = self.snapshots.list_snapshots()
        result_snaps = [s for s in snaps if s["metadata"].get("type") == "analysis_result"]
        all_snap_ids = [s["id"] for s in snaps]
        sel = st.selectbox("Select snapshot to analyze", options=[""] + all_snap_ids)
        if sel:
            meta = self.snapshots.get_snapshot(sel)
            st.write(meta["df"].head())
            if st.button("Run analysis on selected snapshot"):
                result, sid = self.run_analysis(meta["dataset_id"], meta["df"])
                st.success(f"Analysis complete — result snapshot: {sid}")
                st.json(result)
