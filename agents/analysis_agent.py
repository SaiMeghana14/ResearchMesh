import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

class AnalysisAgent:
    def __init__(self, ledger, snapshots):
        self.ledger = ledger
        self.snapshots = snapshots

    def display(self, role):
        st.subheader("📈 Analysis Agent")

        if role == "Guest":
            st.warning("Login required to run analysis.")
            return

        X = np.array(range(10)).reshape(-1, 1)
        y = X.flatten() * 2 + np.random.randint(-2, 2, size=10)

        model = LinearRegression().fit(X, y)
        pred = model.predict(X)

        fig, ax = plt.subplots()
        ax.scatter(X, y, label="Data")
        ax.plot(X, pred, color="red", label="Prediction")
        ax.legend()
        st.pyplot(fig)

        if st.button("Save Snapshot"):
            snap = self.snapshots.create_snapshot("mock-dataset", pred.tolist(), role)
            self.ledger.log(actor=role, action="SAVE_SNAPSHOT", resource="mock-dataset")
            st.success(f"Snapshot saved (ID: {snap['id']})")
