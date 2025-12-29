"""auth.py
Admin authentication module for A.K.A.S.H.A.
Protects sensitive settings/diagnostics behind password authentication.
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Admin password from env or use default (change in production!)
ADMIN_PASSWORD = os.getenv("AKASHA_ADMIN_PASSWORD", "AKASHA_ADMIN_2025")


def init_admin_session():
    """Initialize admin session state."""
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False


def show_admin_login():
    """Show admin login dialog."""
    st.warning("🔐 Admin access required for settings & diagnostics")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        password = st.text_input("Admin Password:", type="password", key="admin_pass_input")
    with col2:
        if st.button("🔓 Unlock"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.success("✅ Admin mode unlocked")
                st.rerun()
            else:
                st.error("❌ Invalid password")


def is_admin_authenticated() -> bool:
    """Check if user is authenticated as admin."""
    return st.session_state.get("admin_authenticated", False)


def require_admin(func):
    """Decorator to wrap functions that require admin auth."""
    def wrapper(*args, **kwargs):
        if not is_admin_authenticated():
            show_admin_login()
            return None
        return func(*args, **kwargs)
    return wrapper


def admin_logout():
    """Logout admin user."""
    st.session_state.admin_authenticated = False
    st.info("🔒 Admin mode locked")
    st.rerun()


__all__ = ["init_admin_session", "is_admin_authenticated", "show_admin_login", "require_admin", "admin_logout"]
