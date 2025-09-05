import streamlit as st
import pandas as pd
from utils.ledger import Ledger

def show_audit_dashboard():
    st.subheader("📜 Audit Dashboard")
    ledger = Ledger()
    logs = ledger.get_logs()

    if not logs:
        st.warning("No audit logs found.")
        return

    df = pd.DataFrame(logs)
    st.dataframe(df)
