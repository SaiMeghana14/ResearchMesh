import streamlit as st
from datetime import datetime

class GovernanceAgent:
    def __init__(self, ledger, snapshots):
        self.ledger = ledger
        self.snapshots = snapshots
        # In-memory consent store (simple demo)
        self.consents = []

    def request_consent(self, owner_email, requester_email, dataset_id, requested_mode):
        cid = f"consent-{int(datetime.utcnow().timestamp()*1000)}"
        rec = {"id": cid, "owner": owner_email, "requester": requester_email, "dataset": dataset_id, "mode": requested_mode, "status": "pending", "created_at": datetime.utcnow().isoformat()}
        self.consents.append(rec)
        self.ledger.log("GovernanceAgent", "consent_requested", rec)
        return rec

    def apply_decision(self, consent_id, decision, actor):
        for c in self.consents:
            if c["id"] == consent_id:
                c["status"] = decision
                c["decided_by"] = actor
                c["decided_at"] = datetime.utcnow().isoformat()
                self.ledger.log("GovernanceAgent", "consent_decided", c)
                # if approved, create anonymized snapshot for requester (demo)
                if decision.startswith("approve"):
                    mode = "anonymized" if "anonymized" in decision else "raw"
                    # fetch dataset via DataAgent behaviour: snapshots object can be used to produce anonymized view
                    df = self.snapshots.get_dataset_anon(c["dataset"])  # implemented in snapshots util
                    sid = self.snapshots.save_snapshot(c["dataset"], df, {"mode": mode, "granted_to": c["requester"], "created_at": datetime.utcnow().isoformat()})
                    self.ledger.log("GovernanceAgent", "consent_grant_snapshot", {"consent_id": consent_id, "snapshot": sid})
                return c
        raise ValueError("Consent not found")

    def render_ui(self, user):
        st.subheader("Governance / Consent Console")
        st.write("Pending consents")
        for c in self.consents:
            if c["status"] == "pending":
                st.write(c)
                # owner action simulated by professor
                if user["email"].endswith("@uni.edu"):
                    if st.button(f"Approve anonymized {c['id']}", key=f"ap_{c['id']}"):
                        self.apply_decision(c["id"], "approve_anonymized", user["email"])
                        st.success("Approved anonymized")
                    if st.button(f"Deny {c['id']}", key=f"deny_{c['id']}"):
                        self.apply_decision(c["id"], "deny", user["email"])
                        st.warning("Denied")
        st.markdown("---")
        st.write("All consents")
        st.write(self.consents)
