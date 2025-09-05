import streamlit as st
import pandas as pd

class DataAgent:
    def __init__(self, ledger, snapshots):
        self.ledger = ledger
        self.snapshots = snapshots
        self.dataset = pd.read_csv("data/sample_datasets.csv")

    def display(self, role):
        st.subheader("📊 Dataset Manager")

        if role == "Guest":
            st.warning("Login required to access datasets.")
            return

        st.dataframe(self.dataset.head())

        if st.button("Log Access"):
            self.ledger.log(actor=role, action="VIEW_DATASET", resource="sample_datasets.csv")
            st.success("Dataset access logged.")
