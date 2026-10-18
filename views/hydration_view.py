import streamlit as st
from datetime import date
from typing import Dict, Any
import database
from services import hydration, health_analyzer

def render_hydration_view(user: Dict[str, Any]):
    st.title("Water & Hydration Tracker")
    st.markdown("Track your daily fluid intake. Consistent hydration supports cognitive performance, digestive motility, and metabolic wellness.")
    
    user_id = user["id"]
    profile_row = database.get_user_profile(user_id)
    today_str = date.today().isoformat()
    
    # Target estimate
    if profile_row:
        p = dict(profile_row)
        summary = health_analyzer.generate_health_summary(p)
        daily_target_ml = summary["hydration_ml"]
    else:
        daily_target_ml = 2500

    today_consumed = database.get_total_hydration_for_date(user_id, today_str)
    stats = hydration.get_hydration_progress(today_consumed, daily_target_ml)

    # Top metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Consumed Today", f"{today_consumed} ml", f"{round(today_consumed/250, 1)} glasses")
    with c2:
        st.metric("Daily Goal", f"{daily_target_ml} ml", f"{round(daily_target_ml/250, 1)} glasses")
    with c3:
        st.metric("Remaining", f"{stats['remaining_ml']} ml", f"{stats['percentage']}% completed")

    # Progress bar
    st.progress(stats["percentage"] / 100.0)
    st.info(stats["status_message"])

    st.markdown("---")
    st.subheader("Log Water Intake")
    
    # Quick Add Buttons
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("💧 +150 ml (Small Cup / Chai)", use_container_width=True):
            database.add_hydration_log(user_id, today_str, 150)
            st.success("Logged 150 ml!")
            st.rerun()
    with q2:
        if st.button("🥛 +250 ml (Standard Glass)", use_container_width=True, type="primary"):
            database.add_hydration_log(user_id, today_str, 250)
            st.success("Logged 250 ml!")
            st.rerun()
    with q3:
        if st.button("🍾 +500 ml (Water Bottle)", use_container_width=True):
            database.add_hydration_log(user_id, today_str, 500)
            st.success("Logged 500 ml!")
            st.rerun()

    # Custom entry
    with st.expander("Enter Custom Amount (ml)", expanded=False):
        with st.form("custom_water_form"):
            custom_ml = st.number_input("Custom Millilitres", min_value=50, max_value=2000, value=300, step=50)
            custom_submitted = st.form_submit_button("Log Amount")
            if custom_submitted:
                database.add_hydration_log(user_id, today_str, int(custom_ml))
                st.success(f"Added {custom_ml} ml!")
                st.rerun()

    st.markdown("---")
    st.subheader("Recent Hydration History")
    history = database.get_hydration_history(user_id, limit_days=7)
    if history:
        st.table([{
            "Date": r["log_date"],
            "Total Fluid (ml)": f"{r['total_ml']} ml",
            "Glasses (~250ml)": round(r["total_ml"] / 250.0, 1)
        } for r in history])
    else:
        st.caption("No past hydration logs yet. Your daily entries will be archived here.")

    st.caption(
        "**Clinical Fluid Restriction Notice:** If you have congestive heart failure, chronic kidney disease (CKD), "
        "or have been prescribed a specific daily fluid restriction by your doctor, prioritize your nephrologist's guidance over generic targets."
    )
