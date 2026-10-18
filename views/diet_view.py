import streamlit as st
from datetime import date
from typing import Dict, Any, List
import database
from services import diet_generator, health_analyzer
import utils

def render_diet_view(user: Dict[str, Any]):
    st.title("My 7-Day Indian Diet Plan")
    st.markdown("Nutritious, authentic Indian meals customized to your dietary pattern, regional preferences, and caloric target.")
    
    user_id = user["id"]
    profile_row = database.get_user_profile(user_id)
    if not profile_row:
        st.info("Please set up your [Health Profile](#my-health-profile) first so we can tailor meals to your preferences.")
        return

    profile = dict(profile_row)
    analysis = health_analyzer.generate_health_summary(profile)

    # Fetch latest saved plan or prompt to generate
    plan_data = database.get_latest_diet_plan(user_id)
    
    col_top1, col_top2 = st.columns([3, 1])
    with col_top1:
        st.write(f"**Dietary Type:** `{profile['diet_type']}` | **Cuisine:** `{profile['regional_cuisine']}` | **Target Calories:** `{analysis['target_calories']} kcal/day`")
    with col_top2:
        if st.button("Regenerate Plan", type="primary", use_container_width=True):
            meals, summary = diet_generator.generate_seven_day_diet_plan(profile, analysis["target_calories"])
            today_str = date.today().isoformat()
            database.save_diet_plan(
                user_id=user_id,
                week_start=today_str,
                calories=summary["daily_avg_calories"],
                protein=summary["daily_avg_protein"],
                carbs=summary["daily_avg_carbs"],
                fat=summary["daily_avg_fat"],
                meals=meals
            )
            st.success("New 7-Day Indian Diet Plan generated successfully!")
            st.rerun()

    if not plan_data:
        st.info("No active diet plan found. Click the button below to generate your personalized 7-Day Indian meal schedule!")
        if st.button("Generate My 7-Day Plan Now", type="primary"):
            meals, summary = diet_generator.generate_seven_day_diet_plan(profile, analysis["target_calories"])
            today_str = date.today().isoformat()
            database.save_diet_plan(
                user_id=user_id,
                week_start=today_str,
                calories=summary["daily_avg_calories"],
                protein=summary["daily_avg_protein"],
                carbs=summary["daily_avg_carbs"],
                fat=summary["daily_avg_fat"],
                meals=meals
            )
            st.success("Plan generated!")
            st.rerun()
        return

    plan_row, meals_list = plan_data

    # Daily Average Summary KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: st.metric("Plan Calories", f"{round(plan_row['target_calories_daily'])} kcal/day")
    with k2: st.metric("Protein", f"{round(plan_row['target_protein_g'])}g/day")
    with k3: st.metric("Carbohydrates", f"{round(plan_row['target_carbs_g'])}g/day")
    with k4: st.metric("Healthy Fats", f"{round(plan_row['target_fat_g'])}g/day")
    with k5:
        csv_data = utils.export_plan_to_csv(plan_row, meals_list)
        st.download_button(
            label="Download Plan (CSV)",
            data=csv_data,
            file_name="fitplate_india_diet_plan.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("---")

    # 7-Day Tabs
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    tabs = st.tabs(days)
    
    for i, day in enumerate(days):
        with tabs[i]:
            day_meals = [m for m in meals_list if m["day_of_week"] == day]
            day_cals = sum(m["calories"] for m in day_meals)
            day_protein = sum(m["protein_g"] for m in day_meals)
            
            st.markdown(f"#### {day} Schedule · <small style='color:#6b7280;'>Total: ~{round(day_cals)} kcal | Protein: ~{round(day_protein, 1)}g</small>", unsafe_allow_html=True)
            
            for m in day_meals:
                meal_id = m["id"]
                is_done = m["is_completed"]
                
                with st.expander(f"{'✅ ' if is_done else '🍽️ '} **{m['meal_slot']}:** {m['food_name']} ({round(m['calories'])} kcal)", expanded=True):
                    mc1, mc2, mc3 = st.columns([3, 2, 2])
                    with mc1:
                        st.write(f"**Portion:** {m['portion_unit']}")
                        st.write(f"**Nutrients:** {round(m['protein_g'], 1)}g Protein | {round(m['carbs_g'], 1)}g Carbs | {round(m['fat_g'], 1)}g Fat | {round(m.get('fiber_g', 0.0), 1)}g Fiber")
                        if m.get("prep_notes"):
                            st.caption(f"**Prep / Recipe:** {m['prep_notes']}")
                        if m.get("substitutions"):
                            st.caption(f"**Affordable Alternative:** {m['substitutions']}")
                    with mc2:
                        st.caption(f"**Allergens:** {m.get('allergens', 'None')}")
                    with mc3:
                        done_toggle = st.checkbox("Mark Eaten", value=is_done, key=f"done_{meal_id}")
                        if done_toggle != is_done:
                            database.update_meal_completion(meal_id, done_toggle)
                            st.rerun()

                        if st.button("Swap This Dish", key=f"swap_{meal_id}", help="Replace with another suitable Indian recipe"):
                            replacement = diet_generator.get_replacement_meal(m["food_name"], m["meal_slot"], profile)
                            if replacement:
                                database.replace_plan_meal(meal_id, replacement)
                                st.success(f"Swapped for {replacement['food_name']}!")
                                st.rerun()
                            else:
                                st.warning("No alternative dish found matching your specific constraints.")

    # Grocery List Section
    st.markdown("---")
    with st.expander("🛒 Weekly Indian Grocery List & Budget Tier", expanded=False):
        groceries = diet_generator.generate_weekly_grocery_list(meals_list, profile.get("food_budget", "Medium / Balanced"))
        st.info(f"**Estimated Weekly Grocery Budget:** {groceries['Estimated Weekly Grocery Cost']}")
        
        gc1, gc2 = st.columns(2)
        with gc1:
            st.markdown("##### 🌾 Whole Grains & Millets")
            for it in groceries["Grains & Millets"]:
                st.markdown(f"- {it}")
            st.markdown("##### 🥬 Fresh Vegetables & Fruits")
            for it in groceries["Fresh Vegetables & Fruits"]:
                st.markdown(f"- {it}")
        with gc2:
            st.markdown("##### 🫘 Lentils, Dairy & Plant Proteins")
            for it in groceries["Proteins & Dairy / Alternatives"]:
                st.markdown(f"- {it}")
            st.markdown("##### 🌰 Nuts, Seeds & Healthy Fats")
            for it in groceries["Nuts, Seeds & Healthy Fats"]:
                st.markdown(f"- {it}")
