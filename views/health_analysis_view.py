import streamlit as st
from typing import Dict, Any
import database
from services import health_analyzer
import utils

def render_health_analysis_view(user: Dict[str, Any]):
    st.title("Health & Metabolic Analysis")
    st.markdown("Clinical estimation of basal metabolic rate, energy expenditure, macronutrient targets, and lifestyle indicators.")
    
    user_id = user["id"]
    profile_row = database.get_user_profile(user_id)
    if not profile_row:
        st.info("Please complete your [Health Profile](#my-health-profile) first to generate your personalized health analysis.")
        return

    profile = dict(profile_row)
    analysis = health_analyzer.generate_health_summary(profile)

    # 1. Safety Alerts
    if analysis["has_safety_block"] or analysis["safety_warnings"]:
        for w in analysis["safety_warnings"]:
            st.warning(f"**Safety Alert:** {w}")

    # 2. Key Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Body Mass Index (BMI)", f"{analysis['bmi']} kg/m²", analysis["bmi_category"])
    with c2:
        st.metric("Basal Metabolic Rate (BMR)", f"{analysis['bmr']} kcal", "Resting energy")
    with c3:
        st.metric("Total Daily Energy (TDEE)", f"{analysis['tdee']} kcal", profile["activity_level"].split("(")[0])
    with c4:
        st.metric("Suggested Daily Calories", f"{analysis['target_calories']} kcal", profile["goal"])

    st.caption(f"**Calorie Strategy:** {analysis['calorie_adjustment_note']}")

    st.markdown("---")

    # 3. Two columns for Detailed Breakdown
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Macronutrient Targets")
        p_g = analysis["target_protein_g"]
        c_g = analysis["target_carbs_g"]
        f_g = analysis["target_fat_g"]
        
        st.markdown(f"""
        - **Protein:** `{p_g}g` (~{round(p_g * 4)} kcal) – Supports muscle recovery and metabolic satiety.
        - **Carbohydrates:** `{c_g}g` (~{round(c_g * 4)} kcal) – Whole grains, millets, fruits, and legumes for sustained energy.
        - **Healthy Fats:** `{f_g}g` (~{round(f_g * 9)} kcal) – Cold-pressed oils, nuts, seeds, and healthy dairy/plant fats.
        - **Dietary Fiber:** Aim for `25g – 35g` daily via vegetables, salads, and unpolished lentils.
        """)

        st.subheader("Hydration & Sleep")
        st.markdown(f"""
        - **Daily Water Target:** `{analysis['hydration_ml']} ml` (~{round(analysis['hydration_ml']/250, 1)} glasses).
        - **Sleep Observation:** {analysis['sleep_observation']}
        """)

    with col_right:
        st.subheader("Understanding Your BMI (Asian-Indian Criteria)")
        st.info(analysis["bmi_description"])

        st.subheader("Educational & Clinical Disclaimer")
        st.caption(
            "Mifflin-St Jeor calculations provide statistical starting estimates. Individual metabolic rates fluctuate with thyroid function, "
            "lean muscle mass, and dietary history. Never pursue crash calorie deficits below safe physiological floors (1,200 kcal for women, 1,500 kcal for men). "
            "If you experience persistent fatigue or dizziness, consult a clinical dietitian or healthcare provider."
        )
