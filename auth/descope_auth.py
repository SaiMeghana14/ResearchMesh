# Mock Descope-like login for demo. Replace with real SDK.
import streamlit as st
import uuid

USERS = {
    "alice@uni.edu": {"name": "Alice", "role": "professor"},
    "bob@student.edu": {"name": "Bob", "role": "student"},
    "carol@external.org": {"name": "Carol", "role": "external"}
}

def login_user():
    st.sidebar.markdown("### Mock login (Descope demo)")
    email = st.sidebar.selectbox("Choose demo user", options=list(USERS.keys()))
    if st.sidebar.button("Login"):
        user = USERS.get(email)
        if not user:
            return None
        token = str(uuid.uuid4())
        user_obj = {"email": email, "name": user["name"], "role": user["role"], "token": token}
        st.session_state["user"] = user_obj
        return user_obj
    # if already in session
    if "user" in st.session_state:
        return st.session_state["user"]
    return None
