import streamlit as st
import threading
import uvicorn

from mcp.mcp_server import create_app  # returns FastAPI app
from auth.descope_auth import descope_login, get_user_role
from utils.ledger import Ledger
from utils.snapshots import SnapshotManager
from agents.data_agent import DataAgent
from agents.analysis_agent import AnalysisAgent
from agents.collab_agent import CollaborationAgent
from agents.governance_agent import GovernanceAgent
from dashboards.audit_dashboard import show_audit_dashboard

# ----------------------------
# Start MCP FastAPI server in background
# ----------------------------
def run_mcp():
    app = create_app()  # FastAPI app
    config = uvicorn.Config(app, host="0.0.0.0", port=8001, log_level="warning")
    server = uvicorn.Server(config)
    server.run()

t = threading.Thread(target=run_mcp, daemon=True)
t.start()

# ----------------------------
# Streamlit App
# ----------------------------
st.set_page_config(page_title="ResearchMesh", layout="wide", initial_sidebar_state="expanded")
st.title("🔬 ResearchMesh — Secure Multi-Agent Research Network")

# ----------------------------
# Authentication (Descope login)
# ----------------------------
user = descope_login()
if not user:
    st.sidebar.error("Please log in with Descope to continue.")
    st.stop()

role = get_user_role()
st.sidebar.success(f"Signed in as {user['name']} ({role})")

# ----------------------------
# Initialize core utilities
# ----------------------------
ledger = Ledger()
snapshots = SnapshotManager()

# Initialize agents
data_agent = DataAgent(ledger=ledger, snapshots=snapshots)
analysis_agent = AnalysisAgent(ledger=ledger, snapshots=snapshots)
collab_agent = CollaborationAgent(ledger=ledger)
gov_agent = GovernanceAgent(ledger=ledger)

# ----------------------------
# Navigation
# ----------------------------
page = st.sidebar.radio(
    "Navigation",
    ["Dataset Access", "Analysis", "Collaboration", "Governance", "Audit Dashboard", "MCP Endpoints"]
)

if page == "Dataset Access":
    data_agent.display(role)

elif page == "Analysis":
    analysis_agent.display(role)

elif page == "Collaboration":
    collab_agent.display(role)

elif page == "Governance":
    gov_agent.display()

elif page == "Audit Dashboard":
    show_audit_dashboard()

elif page == "MCP Endpoints":
    st.subheader("⚡ MCP Server (FastAPI)")
    st.write("Local MCP endpoints are running at: **http://localhost:8001**")
    st.json({
        "endpoints": [
            "/fetch_dataset",
            "/run_analysis",
            "/share_results",
            "/log_access",
            "/request_consent"
        ]
    })
    st.info("This demo runs a local FastAPI server. In production, replace with Cequence MCP proxy + proper OAuth security.")
