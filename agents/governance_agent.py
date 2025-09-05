import streamlit as st

class GovernanceAgent:
    def __init__(self, ledger):
        self.ledger = ledger

    def display(self):
        st.subheader("🛡 Governance Agent")

        user = st.text_input("Enter requesting user:")
        dataset = st.text_input("Dataset name:")

        if st.button("Request Consent"):
            st.success(f"Consent granted to {user} for dataset {dataset}.")
            self.ledger.log(actor=user, action="CONSENT_GRANTED", resource=dataset)
