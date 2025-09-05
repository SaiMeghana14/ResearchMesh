import streamlit as st
import threading
import uvicorn
from mcp.mcp_server import create_app  # returns FastAPI app
from auth.descope_auth import login_user
from utils.ledger import AuditLedger
from utils.snapshots import SnapshotManager
from agents.data_agent import DataAgent
from agents.analysis_agent import AnalysisAgent
from agents.collab_agent import CollaborationAgent
from agents.governance_agent import GovernanceAgent
from dashboards.audit_dashboard import show_audit_dashboard

# Start MCP FastAPI server in background thread
def run_mcp():
    app = create_app()  # FastAPI app
    config = uvicorn.Config(app, host="0.0.0.0", port=8001, log_level="warning")
    server = uvicorn.Server(config)
    server.run()

t = threading.Thread(target=run_mcp, daemon=True)
t.start()

st.set_page_config(page_title="ResearchMesh", layout="wide", initial_sidebar_state="expanded")
st.title("🔬 ResearchMesh — Secure Multi-Agent Research Network")

# Mock auth (replace with Descope integration)
user = login_user()

if not user:
    st.sidebar.error("Login failed (mock).")
    st.stop()

st.sidebar.success(f"Signed in as {user['name']} ({user['role']})")

# Initialize core utilities
ledger = AuditLedger(db_path="researchmesh_ledger.db")
snapshots = SnapshotManager(ledger=ledger)

# Initialize agents
data_agent = DataAgent(ledger=ledger, snapshots=snapshots)
analysis_agent = AnalysisAgent(ledger=ledger, snapshots=snapshots)
collab_agent = CollaborationAgent(ledger=ledger, snapshots=snapshots)
gov_agent = GovernanceAgent(ledger=ledger, snapshots=snapshots)

# Navigation
page = st.sidebar.radio("Navigation", ["Dataset Access", "Analysis", "Collaboration", "Governance", "Audit Dashboard", "MCP Endpoints"])

if page == "Dataset Access":
    data_agent.render_ui(user)
elif page == "Analysis":
    analysis_agent.render_ui(user)
elif page == "Collaboration":
    collab_agent.render_ui(user)
elif page == "Governance":
    gov_agent.render_ui(user)
elif page == "Audit Dashboard":
    show_audit_dashboard(ledger, snapshots)
elif page == "MCP Endpoints":
    st.subheader("MCP Server (FastAPI)")
    st.write("Local MCP endpoints are available at http://localhost:8001")
    st.write("Endpoints: /fetch_dataset, /run_analysis, /share_results, /request_consent")
    st.info("This demo runs a local FastAPI server. Replace with production Cequence + proper security for MCP.")
