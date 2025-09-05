import streamlit as st
from utils.integrations import send_to_slack, send_to_notion

class CollaborationAgent:
    def __init__(self, ledger):
        self.ledger = ledger

    def display(self, role):
        st.subheader("🤝 Collaboration Agent")

        message = st.text_area("Enter research summary:")
        if st.button("Publish to Slack"):
            send_to_slack(message)
            self.ledger.log(actor=role, action="SHARE_RESULT", resource="Slack")
            st.success("Published to Slack!")

        if st.button("Publish to Notion"):
            send_to_notion(message)
            self.ledger.log(actor=role, action="SHARE_RESULT", resource="Notion")
            st.success("Published to Notion!")
