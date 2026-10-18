import streamlit as st
from typing import Dict, Any
import database
from services import exercise_generator

def render_exercise_view(user: Dict[str, Any]):
    st.title("My 7-Day Exercise & Movement Plan")
    st.markdown("Progressive physical activity designed for your fitness level, joint comfort, available time, and home equipment.")
    
    user_id = user["id"]
    profile_row = database.get_user_profile(user_id)
    if not profile_row:
        st.info("Please set up your [Health Profile](#my-health-profile) first to tailor workouts to your joint health and fitness background.")
        return

    profile = dict(profile_row)
    plan_data = database.get_latest_exercise_plan(user_id)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**Experience:** `{profile.get('exercise_experience', 'Beginner')}` | **Equipment:** `{profile.get('equipment', 'None')}` | **Daily Time:** `{profile.get('available_exercise_time_min', 30)} mins`")
        if profile.get("injuries_or_limitations"):
            st.caption(f"**Joint Adaptation Active:** Accommodating `{profile['injuries_or_limitations']}`")
    with col2:
        if st.button("Regenerate Workouts", type="primary", use_container_width=True):
            items = exercise_generator.generate_seven_day_exercise_plan(profile)
            database.save_exercise_plan(user_id, items)
            st.success("New 7-Day exercise plan generated!")
            st.rerun()

    if not plan_data:
        st.info("No workout plan generated yet. Click below to create your 7-Day schedule!")
        if st.button("Generate 7-Day Workout Routine", type="primary"):
            items = exercise_generator.generate_seven_day_exercise_plan(profile)
            database.save_exercise_plan(user_id, items)
            st.success("Workouts ready!")
            st.rerun()
        return

    _, items = plan_data
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    tabs = st.tabs(days)

    for i, day in enumerate(days):
        with tabs[i]:
            day_items = [it for it in items if it["day_of_week"] == day]
            if not day_items:
                st.write("Active recovery day.")
                continue

            for it in day_items:
                item_id = it["id"]
                is_done = it["is_completed"]

                with st.expander(f"{'✅ ' if is_done else '💪 '} **{it['session_title']}:** {it['exercise_name']}", expanded=True):
                    ec1, ec2 = st.columns([3, 2])
                    with ec1:
                        st.markdown(f"**Volume / Sets:** `{it['duration_or_reps']}`")
                        st.markdown(f"**Equipment:** `{it['equipment_needed']}` | **Rest:** `{it['rest_period']}`")
                        st.info(f"**Beginner Modification:** {it['beginner_modification']}")
                        st.markdown(f"**🔥 Warm-up (5 min):** {it['warmup']}")
                        st.markdown(f"**❄️ Cool-down (5 min):** {it['cooldown']}")
                    with ec2:
                        st.warning(f"**Safety Precautions:** {it['safety_instructions']}")
                        done_chk = st.checkbox("Mark Workout Completed", value=is_done, key=f"ex_done_{item_id}")
                        if done_chk != is_done:
                            database.update_exercise_item_completion(item_id, done_chk)
                            st.rerun()
