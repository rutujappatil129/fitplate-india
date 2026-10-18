import streamlit as st
import database
import auth
import config
from views import (
    dashboard_view,
    profile_view,
    health_analysis_view,
    diet_view,
    exercise_view,
    hydration_view,
    progress_view,
    settings_view
)

# Page configuration
st.set_page_config(
    page_title=f"{config.APP_TITLE} – Personalized Indian Diet & Health Analyzer",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    :root {
        --fp-forest: #176b4d;
        --fp-leaf: #2e8b62;
        --fp-ink: #21372e;
        --fp-muted: #68776e;
        --fp-line: #e3e9e2;
        --fp-paper: #fbfcf8;
    }
    .stApp {
        background:
            linear-gradient(rgba(251, 252, 248, .78), rgba(251, 252, 248, .88)),
            url("/app/static/fitplate-food-background.jpg") center / cover fixed;
        color: var(--fp-ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: #f0f5ee;
        border-right: 1px solid var(--fp-line);
    }
    [data-testid="stSidebar"] h2 {
        color: var(--fp-forest);
        font-family: Georgia, "Times New Roman", serif;
    }
    h1, h2, h3 {
        color: var(--fp-ink);
        font-family: Georgia, "Times New Roman", serif;
        letter-spacing: 0;
    }
    [data-testid="stMetric"] {
        background: #fff;
        border: 1px solid var(--fp-line);
        border-radius: 8px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(33, 55, 46, .035);
    }
    [data-testid="stMetricLabel"] { color: var(--fp-muted); }
    [data-testid="stMetricValue"] { color: var(--fp-forest); }
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
        border-radius: 6px;
        transition: transform .16s ease, box-shadow .16s ease;
    }
    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(23, 107, 77, .13);
    }
    [data-testid="stTabs"] button[role="tab"] { color: var(--fp-muted); }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--fp-forest);
        border-bottom-color: var(--fp-leaf);
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--fp-line);
        border-radius: 8px;
    }
    .fitplate-login-hero {
        text-align: center;
        padding: 26px 0 18px;
    }
    .fitplate-login-hero h1 {
        color: var(--fp-forest);
        margin-bottom: 4px;
    }
    .fitplate-login-hero p {
        color: var(--fp-muted);
        margin: 0;
    }
    @media (max-width: 640px) {
        [data-testid="stMetric"] { padding: 12px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize database schema on startup
database.init_db()

# Initialize session state
auth.init_session()

def render_login_register():
    st.markdown(
        f"""
        <div class="fitplate-login-hero">
            <h1>🥗 {config.APP_TITLE}</h1>
            <p>{config.APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        tab_login, tab_register = st.tabs(["🔑 Log In to Your Account", "📝 Register New Account"])
        
        with tab_login:
            st.markdown("##### Welcome Back!")
            st.caption("Access your saved diet plans, hydration history, and body progress.")
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="e.g. rahul@example.com").strip()
                password = st.text_input("Password", type="password")
                btn_login = st.form_submit_button("Log In", type="primary", use_container_width=True)
                
                if btn_login:
                    success, msg, user_data = auth.authenticate_user(email, password)
                    if success:
                        auth.set_current_user(user_data)
                        st.success(f"Welcome back, {user_data['full_name']}!")
                        st.rerun()
                    else:
                        st.error(msg)

        with tab_register:
            st.markdown("##### Create Your FitPlate India Profile")
            if config.IS_HOSTED:
                st.caption("This hosted app stores account and wellness data on its hosting provider. Avoid entering information you do not want stored online.")
            else:
                st.caption("Your health data stays on your computer in a local SQLite database.")
            with st.form("register_form"):
                full_name = st.text_input("Full Name", placeholder="e.g. Ananya Sharma").strip()
                reg_email = st.text_input("Email Address", placeholder="e.g. ananya@example.com").strip()
                reg_pwd = st.text_input("Password (min. 6 characters)", type="password")
                reg_confirm = st.text_input("Confirm Password", type="password")
                
                st.caption("🔒 We use PBKDF2-SHA256 password hashing with unique cryptographic salt. Passwords are never stored in plaintext.")
                btn_register = st.form_submit_button("Create My Account", type="primary", use_container_width=True)
                
                if btn_register:
                    ok, reg_msg, uid = auth.register_user(reg_email, reg_pwd, reg_confirm, full_name)
                    if ok:
                        st.success(f"{reg_msg} Please switch to the 'Log In' tab to continue.")
                    else:
                        st.error(reg_msg)

    st.markdown("---")
    
    # Feature Showcase for Beginners
    st.markdown("### Why FitPlate India?")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown("#### 🍛 Authentic Indian Foods")
        st.caption("Nutritionally accurate recipes across North, South, Maharashtrian, Gujarati, and Pan-Indian cuisines with portion guidance.")
    with f2:
        f2.markdown("#### 🛡️ Diet & Allergy Safety")
        f2.caption("First-class support for Jain Vegetarian (no root veg/garlic), Vegan, Eggetarian, and multi-allergen filtering.")
    with f3:
        f3.markdown("#### 🔬 Science-Based Energy")
        f3.caption("Clinically validated Mifflin-St Jeor equation and Asian-Indian BMI thresholds, with pediatric & pregnancy safety guardrails.")
    with f4:
        if config.IS_HOSTED:
            f4.markdown("#### 🔒 Account-Protected Records")
            f4.caption("Your account data is stored by the hosting provider and separated by user account.")
        else:
            f4.markdown("#### 🔒 Private & Local")
            f4.caption("Runs locally with zero external paid AI API requirements. Your personal health records stay on your machine.")

def main():
    user = auth.get_current_user()

    # Guard: Unauthenticated state
    if not user:
        render_login_register()
        return

    # Navigation helper function
    def navigate_to(page_name: str):
        st.session_state["nav_selection"] = page_name
        st.rerun()

    # Sidebar Navigation
    with st.sidebar:
        st.markdown(f"## 🥗 {config.APP_TITLE}")
        st.caption(config.APP_TAGLINE)
        st.markdown("---")

        user_first = user["full_name"].split()[0]
        st.markdown(f"Logged in as: **{user_first}** ({user['email']})")

        pages = [
            "🏠 Dashboard",
            "👤 My Health Profile",
            "📊 Health Analysis",
            "🥗 My Diet Plan",
            "🏋️ Weekly Exercise Plan",
            "💧 Water Tracker",
            "📈 Progress Tracker",
            "⚙️ Settings & Privacy"
        ]

        # Sync nav selection state
        current_selection = st.session_state.get("nav_selection", "🏠 Dashboard")
        default_index = 0
        for idx, p in enumerate(pages):
            if current_selection in p or p in current_selection:
                default_index = idx
                break

        selected_page = st.radio("Navigation", pages, index=default_index)
        st.session_state["nav_selection"] = selected_page

        st.markdown("---")
        if st.button("🚪 Log Out", use_container_width=True):
            auth.logout_user()
            st.rerun()

    # View Routing
    if "Dashboard" in selected_page:
        dashboard_view.render_dashboard_view(user, navigate_to)
    elif "Health Profile" in selected_page:
        profile_view.render_profile_view(user)
    elif "Health Analysis" in selected_page:
        health_analysis_view.render_health_analysis_view(user)
    elif "Diet Plan" in selected_page:
        diet_view.render_diet_view(user)
    elif "Exercise Plan" in selected_page:
        exercise_view.render_exercise_view(user)
    elif "Water Tracker" in selected_page:
        hydration_view.render_hydration_view(user)
    elif "Progress Tracker" in selected_page:
        progress_view.render_progress_view(user)
    elif "Settings" in selected_page:
        settings_view.render_settings_view(user)

if __name__ == "__main__":
    main()
