import streamlit as st
import descope

# ⚠️ Replace with your actual Descope project values
DESCOPE_PROJECT_ID = "P32HP3Qi9sEBH7pZb6g2jHZ5vCc4"
DESCOPE_CLIENT_ID = "your-client-id"
DESCOPE_CLIENT_SECRET = "your-client-secret"

# Initialize Descope client
try:
    descope_client = descope.DescopeClient(project_id=DESCOPE_PROJECT_ID)
except Exception:
    descope_client = None

if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

def descope_login():
    """Handles user login using Descope (placeholder flow for demo)."""
    if st.session_state["user_info"]:
        return st.session_state["user_info"]

    st.sidebar.subheader("🔑 Login with Descope")

    if st.sidebar.button("Login"):
        # Simulated login response — replace with Descope SDK calls
        st.session_state["user_info"] = {
            "name": "Dr. Alice",
            "role": "Professor",
            "email": "alice@example.com",
            "token": "mock-access-token"
        }
    return st.session_state["user_info"]

def get_user_role():
    """Returns the role of the current user."""
    if st.session_state["user_info"]:
        return st.session_state["user_info"]["role"]
    return "Guest"
