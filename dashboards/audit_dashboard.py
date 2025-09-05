import streamlit as st
import pandas as pd
import altair as alt

def show_audit_dashboard(ledger, snapshots):
    st.header("📜 Audit & Transparency Dashboard")

    # Fetch logs
    logs = ledger.get_logs()
    if not logs:
        st.info("No audit logs yet. Interact with agents to generate activity.")
        return

    df = pd.DataFrame(logs, columns=["Timestamp", "Actor", "Action", "Resource", "Hash"])

    # Show raw table
    with st.expander("🔎 View Raw Audit Logs"):
        st.dataframe(df, use_container_width=True, height=300)

    # Timeline visualization
    st.subheader("📊 Data Flow Timeline")
    chart = (
        alt.Chart(df)
        .mark_circle(size=100)
        .encode(
            x="Timestamp:T",
            y="Actor:N",
            color="Action:N",
            tooltip=["Timestamp", "Actor", "Action", "Resource"],
        )
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

    # Snapshot list
    st.subheader("🗂️ Versioned Snapshots")
    snapshots_list = snapshots.list_snapshots()
    if snapshots_list:
        st.write(pd.DataFrame(snapshots_list, columns=["ID", "Timestamp", "Action", "Details"]))
    else:
        st.info("No snapshots recorded yet.")

    # Ledger verification
    st.subheader("✅ Ledger Integrity Check")
    if st.button("Verify Ledger Chain"):
        if ledger.verify_chain():
            st.success("✔ Ledger is valid. No tampering detected.")
        else:
            st.error("⚠ Ledger integrity check failed. Tampering detected!")
