import streamlit as st
from typing import Dict, Any
import database
import auth
import config

def render_settings_view(user: Dict[str, Any]):
    st.title("Settings & Privacy")
    st.markdown("Manage your account, privacy preferences, and data storage.")
    
    user_id = user["id"]
    profile_row = database.get_user_profile(user_id)
    
    # 1. Account Details
    st.subheader("Account Information")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Name:** {user.get('full_name')}")
        st.write(f"**Email:** {user.get('email')}")
    with c2:
        st.write(f"**User ID:** `{user_id}`")
        st.write(f"**Member Since:** {user.get('created_at', 'Recently')}")

    st.markdown("---")
    
    # 2. Privacy & Data Architecture
    if config.IS_HOSTED:
        st.subheader("🔒 Hosted Data & Account Security")
        st.markdown("""
        - **Hosted SQLite Storage:** Account and health records are stored on the hosting provider's persistent disk, not on your device. Anyone with access to the hosting account or server may be able to access this data.
        - **Password Security:** Your password is protected via **PBKDF2-HMAC-SHA256** key derivation with 100,000 rounds and a unique cryptographic 16-byte salt. Plaintext passwords are never saved.
        - **No Paid AI APIs:** FitPlate India does not require paid external AI APIs.
        - **Multi-Tenant User Isolation:** Every internal database query filters records strictly by `user_id = authenticated_session_id`.
        """)
    else:
        st.subheader("🔒 Privacy & Local Security Notice")
        st.markdown("""
        - **Local SQLite Storage:** Credentials and health records are stored on this computer in a local SQLite database (`fitplate_india.db`).
        - **Password Security:** Your password is protected via **PBKDF2-HMAC-SHA256** key derivation with 100,000 rounds and a unique cryptographic 16-byte salt. Plaintext passwords are never saved.
        - **No Paid AI APIs:** FitPlate India does not require paid external AI APIs.
        - **Multi-Tenant User Isolation:** Every internal database query filters records strictly by `user_id = authenticated_session_id`.
        """)

    st.markdown("---")
    
    # 3. Health & Clinical Disclaimer
    st.subheader("⚠️ Clinical Wellness Disclaimer")
    st.info(config.DISCLAIMER_TEXT)

    st.markdown("---")

    # 4. Account Deletion
    st.subheader("Danger Zone")
    storage_location = "hosted database" if config.IS_HOSTED else "local database"
    st.warning(f"Deleting your account will permanently remove your user credentials, profile, diet plans, workout schedules, hydration logs, and weight history from the {storage_location}.")
    
    confirm_del = st.checkbox("I understand that this action is irreversible and wish to permanently delete my account and all associated records.")
    if st.button("Permanently Delete My Account", type="primary", disabled=not confirm_del):
        database.delete_user_account(user_id)
        auth.logout_user()
        st.success("Your account and all associated data have been completely deleted.")
        st.rerun()
