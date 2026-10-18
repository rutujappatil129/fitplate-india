import streamlit as st
from datetime import date
from typing import Dict, Any
import database
from services import progress

def render_progress_view(user: Dict[str, Any]):
    st.title("Weight & Progress Tracker")
    st.markdown("Track your body weight trajectory over time with objective milestone benchmarks.")
    
    user_id = user["id"]
    profile_row = database.get_user_profile(user_id)
    target_weight = float(profile_row["target_weight_kg"]) if profile_row else 65.0

    # 1. Log Today's Weight Form
    with st.expander("📝 Log Today's Weight & Measurements", expanded=True):
        with st.form("log_weight_form"):
            w_col1, w_col2, w_col3 = st.columns(3)
            with w_col1:
                log_date = st.date_input("Date", value=date.today()).isoformat()
            with w_col2:
                weight_val = st.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=float(profile_row["current_weight_kg"]) if profile_row else 70.0, step=0.1)
            with w_col3:
                waist_val = st.number_input("Waist Circumference (cm, Optional)", min_value=0.0, max_value=200.0, value=0.0, step=0.5)

            notes = st.text_input("Notes (e.g. morning weigh-in after fasting, post-workout, etc.)", placeholder="Optional notes")
            save_wt = st.form_submit_button("Record Entry", type="primary", use_container_width=True)

            if save_wt:
                database.add_weight_log(
                    user_id=user_id,
                    log_date=log_date,
                    weight_kg=weight_val,
                    waist_cm=waist_val if waist_val > 0 else None,
                    notes=notes.strip()
                )
                if profile_row:
                    updated_p = dict(profile_row)
                    updated_p["current_weight_kg"] = weight_val
                    database.upsert_user_profile(user_id, updated_p)
                st.success(f"Recorded {weight_val} kg on {log_date}!")
                st.rerun()

    # 2. Analytics & Interactive Plotly Chart
    logs = database.get_weight_logs(user_id)
    analytics = progress.compute_weight_analytics(logs, target_weight)

    if analytics["has_data"]:
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Initial Logged Weight", f"{analytics['start_weight']} kg")
        with m2: st.metric("Latest Weight", f"{analytics['current_weight']} kg")
        with m3: st.metric("Net Change", f"{analytics['weight_change']:+} kg")
        with m4: st.metric("Distance to Target", f"{analytics['distance_to_target']} kg", f"Goal: {target_weight} kg")

    fig = progress.create_weight_trend_chart(logs, target_weight)
    st.plotly_chart(fig, use_container_width=True)

    # 3. Healthy Mindset Educational Message
    st.info(
        "💡 **Wellness Insight:** Human body weight fluctuates naturally by 0.5 to 2.0 kg day-to-day due to water retention, "
        "glycogen storage, sodium intake, hormonal shifts, and digestive volume. Look at the general multi-week trend "
        "rather than worrying about individual daily fluctuations."
    )

    # 4. Historical Logs Table with Delete Action
    if logs:
        st.subheader("Historical Weight Logs")
        for entry in reversed(logs):
            e_id = entry["id"]
            waist_text = f"{entry['waist_cm']} cm" if entry.get("waist_cm") else "—"
            c_date, c_wt, c_waist, c_notes, c_del = st.columns([2, 2, 2, 3, 1])
            with c_date: st.write(f"📅 **{entry['log_date']}**")
            with c_wt: st.write(f"⚖️ `{entry['weight_kg']} kg`")
            with c_waist: st.write(f"📏 {waist_text}")
            with c_notes: st.caption(entry.get("notes") or "")
            with c_del:
                if st.button("🗑️", key=f"del_wt_{e_id}", help="Delete entry"):
                    database.delete_weight_log(e_id, user_id)
                    st.rerun()
