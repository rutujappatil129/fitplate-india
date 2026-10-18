import streamlit as st
from datetime import date
from typing import Dict, Any
import database
from services import health_analyzer, hydration, progress
import utils

def render_dashboard_view(user: Dict[str, Any], navigate_to):
    user_id = user["id"]
    profile_row = database.get_user_profile(user_id)
    today_str = date.today().isoformat()
    today_name = date.today().strftime("%A")

    # Welcome Header
    first_name = user["full_name"].split()[0]
    st.title(f"Namaste, {first_name}! 🙏")
    st.markdown("Welcome to your personal wellness command center. Here is your daily overview.")

    if not profile_row:
        st.warning("⚠️ **Your Health Profile is incomplete.** Please complete your profile to unlock customized diet plans, BMR calculations, and workout schedules.")
        if st.button("Complete My Profile Now", type="primary"):
            navigate_to("My Health Profile")
        return

    profile = dict(profile_row)
    analysis = health_analyzer.generate_health_summary(profile)

    # 1. Health Safety Flags Banner
    if analysis["has_safety_block"] or analysis["safety_warnings"]:
        with st.container():
            for w in analysis["safety_warnings"]:
                st.warning(f"**Health Caution:** {w}")

    # 2. Top KPI Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Current Weight", f"{profile['current_weight_kg']} kg", f"Goal: {profile['target_weight_kg']} kg")
    with c2:
        st.metric("BMI", f"{analysis['bmi']} kg/m²", analysis["bmi_category"])
    with c3:
        st.metric("Daily Energy Target", f"{analysis['target_calories']} kcal", profile["goal"])
    with c4:
        consumed_water = database.get_total_hydration_for_date(user_id, today_str)
        water_stats = hydration.get_hydration_progress(consumed_water, analysis["hydration_ml"])
        st.metric("Hydration Today", f"{consumed_water} ml", f"{water_stats['percentage']}% of {analysis['hydration_ml']} ml")

    st.markdown("---")

    # 3. Quick Action Buttons Row
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("🥗 View 7-Day Diet Plan", use_container_width=True):
            navigate_to("My Diet Plan")
    with q2:
        if st.button("💪 View Workout Plan", use_container_width=True):
            navigate_to("Weekly Exercise Plan")
    with q3:
        if st.button("💧 Log Water Intake", use_container_width=True):
            navigate_to("Water Tracker")
    with q4:
        if st.button("⚖️ Record Today's Weight", use_container_width=True):
            navigate_to("Progress Tracker")

    st.markdown("---")

    # 4. Two columns: Today's Meals & Today's Workout
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader(f"🍽️ Today's Meals ({today_name})")
        plan_data = database.get_latest_diet_plan(user_id)
        if plan_data:
            _, meals_list = plan_data
            today_meals = [m for m in meals_list if m["day_of_week"] == today_name]
            if today_meals:
                for m in today_meals:
                    meal_id = m["id"]
                    is_done = m["is_completed"]
                    m_col1, m_col2 = st.columns([4, 1])
                    with m_col1:
                        st.markdown(f"**{m['meal_slot']}:** {m['food_name']} (`{round(m['calories'])} kcal`)")
                        st.caption(f"{m['portion_unit']} · {round(m['protein_g'], 1)}g Protein")
                    with m_col2:
                        chk = st.checkbox("Done", value=is_done, key=f"dash_meal_{meal_id}")
                        if chk != is_done:
                            database.update_meal_completion(meal_id, chk)
                            st.rerun()
            else:
                st.caption(f"No meals scheduled for {today_name}.")
        else:
            st.info("No active meal plan. Generate one in the 'My Diet Plan' page.")
            if st.button("Generate Diet Plan", key="dash_gen_diet"):
                navigate_to("My Diet Plan")

    with right_col:
        st.subheader(f"🏃 Today's Exercise ({today_name})")
        ex_data = database.get_latest_exercise_plan(user_id)
        if ex_data:
            _, ex_items = ex_data
            today_exercises = [it for it in ex_items if it["day_of_week"] == today_name]
            if today_exercises:
                for it in today_exercises:
                    it_id = it["id"]
                    is_done = it["is_completed"]
                    st.markdown(f"**{it['session_title']}**")
                    st.markdown(f"**Activity:** {it['exercise_name']}")
                    st.caption(f"Volume: {it['duration_or_reps']} | Rest: {it['rest_period']}")
                    st.info(f"**Modification:** {it['beginner_modification']}")
                    ex_chk = st.checkbox("Workout Completed", value=is_done, key=f"dash_ex_{it_id}")
                    if ex_chk != is_done:
                        database.update_exercise_item_completion(it_id, ex_chk)
                        st.rerun()
            else:
                st.caption(f"Rest & Recovery scheduled for {today_name}.")
        else:
            st.info("No workout routine generated yet.")
            if st.button("Create Exercise Plan", key="dash_gen_ex"):
                navigate_to("Weekly Exercise Plan")

    st.markdown("---")

    # 5. Daily Habit Checklist & Weight Trend Preview
    h_col, w_col = st.columns([1, 1])
    
    with h_col:
        st.subheader("✅ Daily Habit Checklist")
        habit_row = database.get_habit_log_for_date(user_id, today_str)
        curr_habit = habit_row or {}

        with st.form("dash_habit_form"):
            sleep_h = st.number_input("Sleep Last Night (Hours)", min_value=0.0, max_value=16.0, value=float(curr_habit.get("sleep_hours", profile.get("sleep_duration_hours", 7.5))), step=0.5)
            h_diet = st.checkbox("Followed healthy nutrition plan today", value=bool(curr_habit.get("diet_followed", False)))
            h_veggies = st.checkbox("Ate fresh vegetables / whole fruit / salad", value=bool(curr_habit.get("fruits_veggies_consumed", False)))
            h_exercise = st.checkbox("Completed planned physical movement", value=bool(curr_habit.get("exercise_completed", False)))
            h_steps = st.number_input("Daily Steps (Optional)", min_value=0, max_value=50000, value=int(curr_habit.get("daily_steps", 6000)), step=500)
            h_mood = st.slider("Energy / Mood Rating (1 to 10)", min_value=1, max_value=10, value=int(curr_habit.get("mood_rating", 7)))

            save_habit = st.form_submit_button("Save Daily Habits", type="primary")
            if save_habit:
                database.save_habit_log(user_id, today_str, {
                    "sleep_hours": sleep_h,
                    "diet_followed": h_diet,
                    "fruits_veggies_consumed": h_veggies,
                    "exercise_completed": h_exercise,
                    "daily_steps": h_steps,
                    "mood_rating": h_mood
                })
                st.success("Habits logged for today!")
                st.rerun()

    with w_col:
        st.subheader("📈 Weight Progress Trend")
        w_logs = database.get_weight_logs(user_id)
        if w_logs:
            fig = progress.create_weight_trend_chart(w_logs, float(profile["target_weight_kg"]))
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No weight logs recorded yet.")
            if st.button("Log Your First Weight", key="dash_first_wt"):
                navigate_to("Progress Tracker")
