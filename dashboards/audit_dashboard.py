import streamlit as st
import plotly.express as px
import pandas as pd

def show_audit_dashboard(ledger, snapshots):
    st.subheader("Audit & Transparency Dashboard")
    df_ledger = ledger.recent(limit=200)
    if df_ledger.empty:
        st.info("No ledger entries yet.")
        return
    # parse details as column for display
    df_ledger["details_str"] = df_ledger["details"].apply(lambda x: x if isinstance(x, str) else str(x))
    st.dataframe(df_ledger[["timestamp", "actor", "action", "details_str"]].head(200), height=300)
    # simple timeline by action counts
    action_counts = df_ledger.groupby("action").size().reset_index(name="count")
    fig = px.bar(action_counts, x="action", y="count", title="Action counts")
    st.plotly_chart(fig, use_container_width=True)
    # snapshots summary
    snaps = snapshots.list_snapshots()
    st.write(f"Snapshots: {len(snaps)}")
    if snaps:
        snap_df = pd.DataFrame([{"id": s["id"], "dataset_id": s["dataset_id"], "metadata": s["metadata"], "created_at": s.get("created_at")} for s in snaps])
        st.dataframe(snap_df, height=200)
