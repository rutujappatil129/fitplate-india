import hashlib
import os
import re
import secrets
from typing import Optional, Tuple, Dict, Any
import streamlit as st
import database

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Hashes password securely using PBKDF2-HMAC-SHA256 with a unique cryptographic salt.
    100,000 iterations for defense against brute-force attacks.
    """
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100000
    )
    return key.hex(), salt

def verify_password(plain_password: str, stored_hash: str, salt: str) -> bool:
    """Verifies a plain password against the stored PBKDF2 hash and salt."""
    key = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100000
    )
    return secrets.compare_digest(key.hex(), stored_hash)

def validate_registration_inputs(email: str, password: str, confirm_password: str, full_name: str) -> Tuple[bool, str]:
    """Validates user input fields before registration."""
    if not full_name or len(full_name.strip()) < 2:
        return False, "Full name must be at least 2 characters long."
    if not email or not EMAIL_REGEX.match(email.strip()):
        return False, "Please enter a valid email address (e.g., name@example.com)."
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if password != confirm_password:
        return False, "Passwords do not match. Please re-enter."
    return True, ""

def register_user(email: str, password: str, confirm_password: str, full_name: str, db_path: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
    """Registers a new user, hashes password, and creates initial database records."""
    valid, err = validate_registration_inputs(email, password, confirm_password, full_name)
    if not valid:
        return False, err, None
    
    # Check duplicate
    existing = database.get_user_by_email(email, db_path=db_path)
    if existing:
        return False, "An account with this email address already exists. Please log in.", None

    pwd_hash, salt = hash_password(password)
    user_id = database.create_user(email, pwd_hash, salt, full_name, db_path=db_path)
    if not user_id:
        return False, "Failed to create account due to a database conflict.", None

    return True, "Account registered successfully! You can now log in.", user_id

def authenticate_user(email: str, password: str, db_path: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Authenticates credentials against the database."""
    if not email or not password:
        return False, "Please provide both email and password.", None
    
    user = database.get_user_by_email(email, db_path=db_path)
    if not user:
        return False, "Invalid email or password.", None

    if not verify_password(password, user["password_hash"], user["salt"]):
        return False, "Invalid email or password.", None

    user_dict = {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "created_at": user["created_at"]
    }
    return True, "Authentication successful.", user_dict

# Session state helpers for Streamlit
def init_session():
    """Initializes authentication state in Streamlit session."""
    if "authenticated_user" not in st.session_state:
        st.session_state["authenticated_user"] = None

def get_current_user() -> Optional[Dict[str, Any]]:
    return st.session_state.get("authenticated_user")

def set_current_user(user: Dict[str, Any]):
    st.session_state["authenticated_user"] = user

def logout_user():
    st.session_state["authenticated_user"] = None
    # Clear any cached plans or state
    for k in ["active_plan", "diet_plan_id", "exercise_plan_id"]:
        if k in st.session_state:
            del st.session_state[k]

def is_authenticated() -> bool:
    return st.session_state.get("authenticated_user") is not None
