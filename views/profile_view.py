import streamlit as st
from typing import Dict, Any
import database
import config

def render_profile_view(user: Dict[str, Any]):
    st.title("My Health Profile")
    st.markdown("Customize your physiological metrics, lifestyle habits, and dietary preferences for clinically sound personalization.")
    
    user_id = user["id"]
    existing_profile = database.get_user_profile(user_id)
    p = dict(existing_profile) if existing_profile else {}

    with st.form("health_profile_form"):
        st.subheader("1. Personal & Physical Metrics")
        st.caption("We collect the minimum physiological information required to estimate your basal metabolic rate (Mifflin-St Jeor formula).")
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age (Years)", min_value=12, max_value=100, value=int(p.get("age", 25)), step=1)
            sex = st.selectbox(
                "Physiological Sex (Used for BMR equation)",
                ["Male", "Female"],
                index=0 if p.get("sex", "Male") == "Male" else 1,
                help="BMR calculation formulas (Mifflin-St Jeor) use biological sex to estimate baseline energy expenditure."
            )
            gender_identity = st.text_input("Gender Identity (Optional, for respectful personalization)", value=p.get("gender_identity", ""))
            height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=float(p.get("height_cm", 170.0)), step=0.5)

        with col2:
            current_weight = st.number_input("Current Weight (kg)", min_value=30.0, max_value=250.0, value=float(p.get("current_weight_kg", 70.0)), step=0.5)
            target_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=250.0, value=float(p.get("target_weight_kg", 65.0)), step=0.5)
            goal = st.selectbox(
                "Primary Goal",
                config.GOAL_OPTIONS,
                index=config.GOAL_OPTIONS.index(p.get("goal", "Lose Weight")) if p.get("goal") in config.GOAL_OPTIONS else 0
            )
            activity_level = st.selectbox(
                "Daily Activity Level",
                config.ACTIVITY_LEVELS,
                index=config.ACTIVITY_LEVELS.index(p.get("activity_level", config.ACTIVITY_LEVELS[2])) if p.get("activity_level") in config.ACTIVITY_LEVELS else 2
            )

        st.markdown("---")
        st.subheader("2. Indian Diet & Nutritional Preferences")
        
        col3, col4 = st.columns(2)
        with col3:
            diet_type = st.selectbox(
                "Dietary Pattern",
                config.DIET_TYPES,
                index=config.DIET_TYPES.index(p.get("diet_type", "Vegetarian")) if p.get("diet_type") in config.DIET_TYPES else 0
            )
            regional_cuisine = st.selectbox(
                "Regional Cuisine Preference",
                config.REGIONAL_CUISINES,
                index=config.REGIONAL_CUISINES.index(p.get("regional_cuisine", "Pan-Indian")) if p.get("regional_cuisine") in config.REGIONAL_CUISINES else 0
            )
            food_budget = st.selectbox(
                "Food Budget Preference",
                config.BUDGET_LEVELS,
                index=config.BUDGET_LEVELS.index(p.get("food_budget", config.BUDGET_LEVELS[1])) if p.get("food_budget") in config.BUDGET_LEVELS else 1
            )
            meals_per_day = st.slider("Meals per Day", min_value=3, max_value=6, value=int(p.get("meals_per_day", 5)))

        with col4:
            current_allergies = [a.strip() for a in p.get("allergies", "").split(",") if a.strip()]
            allergies = st.multiselect(
                "Food Allergies / Serious Sensitivities",
                config.COMMON_ALLERGENS,
                default=[a for a in current_allergies if a in config.COMMON_ALLERGENS]
            )
            disliked_foods = st.text_input("Foods Disliked (Comma-separated, e.g. Bitter gourd, Mushrooms)", value=p.get("disliked_foods", ""))
            liked_foods = st.text_input("Foods Especially Liked (Optional)", value=p.get("liked_foods", ""))
            religious_restrictions = st.text_input("Special Dietary Restrictions (Optional)", value=p.get("religious_restrictions", ""))

        st.markdown("---")
        st.subheader("3. Lifestyle & Physical Activity")
        col5, col6 = st.columns(2)
        with col5:
            sleep_hours = st.slider("Average Daily Sleep (Hours)", min_value=4.0, max_value=12.0, value=float(p.get("sleep_duration_hours", 7.5)), step=0.5)
            exercise_experience = st.selectbox(
                "Exercise Experience",
                config.FITNESS_LEVELS,
                index=config.FITNESS_LEVELS.index(p.get("exercise_experience", "Beginner")) if p.get("exercise_experience") in config.FITNESS_LEVELS else 0
            )
        with col6:
            exercise_time = st.select_slider(
                "Available Workout Time per Day (Minutes)",
                options=[15, 20, 30, 45, 60],
                value=int(p.get("available_exercise_time_min", 30))
            )
            equipment = st.selectbox(
                "Exercise Equipment Available",
                config.EQUIPMENT_OPTIONS,
                index=config.EQUIPMENT_OPTIONS.index(p.get("equipment", config.EQUIPMENT_OPTIONS[0])) if p.get("equipment") in config.EQUIPMENT_OPTIONS else 0
            )

        st.markdown("---")
        st.subheader("4. Health & Medical Safeguards")
        st.caption("Your health safety is our priority. Disclosing conditions helps us ensure we do not recommend unsafe caloric deficits.")
        
        is_pregnant_or_lactating = st.checkbox("Currently pregnant or breastfeeding (Lactating)", value=bool(p.get("is_pregnant_or_lactating", False)))
        medical_conditions = st.text_area(
            "Medical Conditions (Optional, e.g. Diabetes, Kidney disease, Heart disease, History of eating disorders)",
            value=p.get("medical_conditions", ""),
            placeholder="Type 'None' or leave blank if you have no diagnosed medical conditions."
        )
        injuries = st.text_input(
            "Injuries or Movement Restrictions (e.g., Knee pain, Lower back pain, Shoulder injury)",
            value=p.get("injuries_or_limitations", ""),
            placeholder="e.g. Mild knee stiffness when bending"
        )

        submitted = st.form_submit_button("Save Health Profile", use_container_width=True, type="primary")
        if submitted:
            profile_data = {
                "age": age,
                "sex": sex,
                "gender_identity": gender_identity.strip(),
                "height_cm": height_cm,
                "current_weight_kg": current_weight,
                "target_weight_kg": target_weight,
                "goal": goal,
                "activity_level": activity_level,
                "diet_type": diet_type,
                "regional_cuisine": regional_cuisine,
                "allergies": ", ".join(allergies),
                "intolerances": "",
                "liked_foods": liked_foods.strip(),
                "disliked_foods": disliked_foods.strip(),
                "religious_restrictions": religious_restrictions.strip(),
                "medical_conditions": medical_conditions.strip(),
                "is_pregnant_or_lactating": is_pregnant_or_lactating,
                "injuries_or_limitations": injuries.strip(),
                "food_budget": food_budget,
                "meals_per_day": meals_per_day,
                "preferred_meal_times": "",
                "sleep_duration_hours": sleep_hours,
                "exercise_experience": exercise_experience,
                "available_exercise_time_min": exercise_time,
                "equipment": equipment
            }
            database.upsert_user_profile(user_id, profile_data)
            # Clear cached plans so regeneration will use new parameters
            if "active_plan" in st.session_state:
                del st.session_state["active_plan"]
            st.success("Your health profile has been successfully saved! Head over to 'Health Analysis' or 'Dashboard' to view your recommendations.")
            st.rerun()
