import streamlit as st
from datetime import datetime
import json

from utils.integrations import post_to_channel

class CollaborationAgent:
    def __init__(self, ledger, snapshots):
        self.ledger = ledger
        self.snapshots = snapshots

    def share(self, result, channels, snapshot_meta):
        self.ledger.log("CollabAgent", "share_start", {"channels": channels, "snapshot_meta": snapshot_meta})
        out = {}
        for ch in channels:
            out[ch] = post_to_channel(ch, result.get("summary", "(no summary)"))
        self.ledger.log("CollabAgent", "share_end", {"channels": channels, "snapshot": snapshot_meta})
        return out

    def render_ui(self, user):
        st.subheader("Share Analysis Results")
        snaps = self.snapshots.list_snapshots()
        result_snaps = [s for s in snaps if s["metadata"].get("type") == "analysis_result"]
        sel = st.selectbox("Choose result snapshot", options=[""] + [s["id"] for s in result_snaps])
        if sel:
            meta = self.snapshots.get_snapshot(sel)
            result = meta["df"].iloc[0]["result"]
            try:
                result = json.loads(result)
            except Exception:
                result = {"summary": str(result)}
            st.write("Result summary:")
            st.write(result.get("summary"))
            channels = st.multiselect("Channels to share", options=["notion", "slack", "teams", "github"])
            if st.button("Share"):
                out = self.share(result, channels, meta["metadata"])
                st.success("Shared to channels")
                st.write(out)
