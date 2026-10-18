import io
import csv
from typing import List, Dict, Any, Tuple
from datetime import datetime

def format_kcal(val: float) -> str:
    return f"{round(val):,} kcal"

def format_grams(val: float) -> str:
    return f"{round(val, 1)}g"

def cm_to_ft_in(cm: float) -> str:
    total_inches = cm / 2.54
    feet = int(total_inches // 12)
    inches = int(round(total_inches % 12))
    return f"{feet} ft {inches} in"

def kg_to_lbs(kg: float) -> float:
    return round(kg * 2.20462, 1)

def export_plan_to_csv(plan_row: Any, meals_list: List[Any]) -> str:
    """Generates a downloadable CSV string for a 7-day diet plan."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header summary
    writer.writerow(["FitPlate India - 7-Day Personalized Diet Plan"])
    writer.writerow(["Target Daily Calories", f"{plan_row['target_calories_daily']} kcal"])
    writer.writerow(["Target Protein", f"{plan_row['target_protein_g']} g"])
    writer.writerow(["Target Carbs", f"{plan_row['target_carbs_g']} g"])
    writer.writerow(["Target Fat", f"{plan_row['target_fat_g']} g"])
    writer.writerow([])
    
    # Detailed meals
    writer.writerow([
        "Day of Week", "Meal Slot", "Dish Name", "Portion Unit",
        "Calories (kcal)", "Protein (g)", "Carbs (g)", "Fat (g)", "Fiber (g)",
        "Preparation Instructions", "Substitutions", "Allergen Notes"
    ])
    
    for m in meals_list:
        writer.writerow([
            m["day_of_week"],
            m["meal_slot"],
            m["food_name"],
            m["portion_unit"],
            round(m["calories"], 1),
            round(m["protein_g"], 1),
            round(m["carbs_g"], 1),
            round(m["fat_g"], 1),
            round(m.get("fiber_g", 0.0), 1),
            m.get("prep_notes", ""),
            m.get("substitutions", ""),
            m.get("allergens", "None")
        ])
    
    return output.getvalue()
