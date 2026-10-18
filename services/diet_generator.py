import csv
import random
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from config import FOODS_CSV_PATH, MEAL_SLOTS

def load_foods_database(csv_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = Path(csv_path) if csv_path else FOODS_CSV_PATH
    if not path.exists():
        return []
    
    foods = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            foods.append({
                "food_id": row["food_id"],
                "name": row["name"],
                "meal_slot": row["meal_slot"],
                "diet_type": row["diet_type"],
                "regional_cuisine": row["regional_cuisine"],
                "is_jain_safe": row["is_jain_safe"].strip().lower() in ["true", "1", "yes"],
                "is_vegan_safe": row["is_vegan_safe"].strip().lower() in ["true", "1", "yes"],
                "allergens": row["allergens"],
                "portion_unit": row["portion_unit"],
                "portion_size_g": float(row["portion_size_g"]),
                "calories": float(row["calories"]),
                "protein_g": float(row["protein_g"]),
                "carbs_g": float(row["carbs_g"]),
                "fat_g": float(row["fat_g"]),
                "fiber_g": float(row["fiber_g"]),
                "substitutions": row["substitutions"],
                "prep_notes": row["prep_notes"]
            })
    return foods

def filter_foods_for_user(foods: List[Dict[str, Any]], profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filters the food catalog strictly adhering to diet type, allergies, and dislikes."""
    diet_type = profile.get("diet_type", "Vegetarian").strip()
    allergies = [a.strip().lower() for a in profile.get("allergies", "").split(",") if a.strip()]
    dislikes = [d.strip().lower() for d in profile.get("disliked_foods", "").split(",") if d.strip()]
    
    filtered = []
    for f in foods:
        # 1. Diet Type Checks
        if diet_type == "Vegan":
            if not f["is_vegan_safe"] or f["diet_type"] in ["Non-Vegetarian", "Eggetarian"]:
                continue
        elif diet_type == "Jain Vegetarian":
            if not f["is_jain_safe"] or f["diet_type"] in ["Non-Vegetarian", "Eggetarian"]:
                continue
        elif diet_type == "Vegetarian":
            if f["diet_type"] in ["Non-Vegetarian", "Eggetarian"]:
                continue
        elif diet_type == "Eggetarian":
            if f["diet_type"] == "Non-Vegetarian":
                continue

        # 2. Allergies Check
        dish_allergens = f["allergens"].lower()
        has_allergen = False
        for a in allergies:
            if ("dairy" in a or "lactose" in a) and ("dairy" in dish_allergens or "lactose" in dish_allergens):
                has_allergen = True; break
            if ("gluten" in a or "wheat" in a) and ("gluten" in dish_allergens or "wheat" in dish_allergens):
                has_allergen = True; break
            if ("nut" in a or "peanut" in a) and ("nut" in dish_allergens or "peanut" in dish_allergens):
                has_allergen = True; break
            if "soy" in a and "soy" in dish_allergens:
                has_allergen = True; break
            if "egg" in a and "egg" in dish_allergens:
                has_allergen = True; break
            if "fish" in a and ("fish" in dish_allergens or "seafood" in dish_allergens):
                has_allergen = True; break
        if has_allergen:
            continue

        # 3. Disliked Foods Check
        dish_name_lower = f["name"].lower()
        if any(d in dish_name_lower for d in dislikes):
            continue

        filtered.append(f)
    return filtered

def generate_seven_day_diet_plan(profile: Dict[str, Any], target_calories: float) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    all_foods = load_foods_database()
    eligible_foods = filter_foods_for_user(all_foods, profile)
    
    if not eligible_foods:
        eligible_foods = all_foods

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    preferred_cuisine = profile.get("regional_cuisine", "Pan-Indian")
    
    meals_count = profile.get("meals_per_day", 5)
    if meals_count <= 3:
        slots = ["Breakfast", "Lunch", "Dinner"]
    elif meals_count == 4:
        slots = ["Breakfast", "Lunch", "Evening Snack", "Dinner"]
    elif meals_count == 5:
        slots = ["Early Morning", "Breakfast", "Lunch", "Evening Snack", "Dinner"]
    else:
        slots = ["Early Morning", "Breakfast", "Mid-Morning Snack", "Lunch", "Evening Snack", "Dinner"]

    meals_by_slot = {s: [] for s in slots}
    for f in eligible_foods:
        if f["meal_slot"] in meals_by_slot:
            meals_by_slot[f["meal_slot"]].append(f)

    for s in slots:
        if not meals_by_slot[s]:
            meals_by_slot[s] = [f for f in all_foods if f["meal_slot"] == s]

    plan_meals = []
    total_plan_cals = 0.0
    total_plan_protein = 0.0
    total_plan_carbs = 0.0
    total_plan_fat = 0.0
    total_plan_fiber = 0.0

    for day in days:
        for slot in slots:
            options = meals_by_slot[slot]
            regional_matches = [o for o in options if o["regional_cuisine"] == preferred_cuisine]
            pool = regional_matches if len(regional_matches) >= 2 else options
            
            chosen = random.choice(pool) if pool else options[0]
            
            plan_meals.append({
                "day_of_week": day,
                "meal_slot": slot,
                "food_name": chosen["name"],
                "portion_unit": chosen["portion_unit"],
                "portion_size_g": chosen["portion_size_g"],
                "calories": chosen["calories"],
                "protein_g": chosen["protein_g"],
                "carbs_g": chosen["carbs_g"],
                "fat_g": chosen["fat_g"],
                "fiber_g": chosen["fiber_g"],
                "prep_notes": chosen["prep_notes"],
                "substitutions": chosen["substitutions"],
                "allergens": chosen["allergens"],
                "is_completed": False
            })
            total_plan_cals += chosen["calories"]
            total_plan_protein += chosen["protein_g"]
            total_plan_carbs += chosen["carbs_g"]
            total_plan_fat += chosen["fat_g"]
            total_plan_fiber += chosen["fiber_g"]

    daily_avg_cals = round(total_plan_cals / 7.0)
    daily_avg_protein = round(total_plan_protein / 7.0, 1)
    daily_avg_carbs = round(total_plan_carbs / 7.0, 1)
    daily_avg_fat = round(total_plan_fat / 7.0, 1)
    daily_avg_fiber = round(total_plan_fiber / 7.0, 1)

    nutritional_summary = {
        "daily_avg_calories": daily_avg_cals,
        "daily_avg_protein": daily_avg_protein,
        "daily_avg_carbs": daily_avg_carbs,
        "daily_avg_fat": daily_avg_fat,
        "daily_avg_fiber": daily_avg_fiber,
        "target_calories": round(target_calories),
        "is_calorie_balanced": abs(daily_avg_cals - target_calories) < 250
    }

    return plan_meals, nutritional_summary

def get_replacement_meal(current_food_name: str, meal_slot: str, profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    all_foods = load_foods_database()
    eligible = filter_foods_for_user(all_foods, profile)
    slot_options = [f for f in eligible if f["meal_slot"] == meal_slot and f["name"] != current_food_name]
    
    if not slot_options:
        slot_options = [f for f in all_foods if f["meal_slot"] == meal_slot and f["name"] != current_food_name]
        
    if slot_options:
        chosen = random.choice(slot_options)
        return {
            "food_name": chosen["name"],
            "portion_unit": chosen["portion_unit"],
            "portion_size_g": chosen["portion_size_g"],
            "calories": chosen["calories"],
            "protein_g": chosen["protein_g"],
            "carbs_g": chosen["carbs_g"],
            "fat_g": chosen["fat_g"],
            "fiber_g": chosen["fiber_g"],
            "prep_notes": chosen["prep_notes"],
            "substitutions": chosen["substitutions"],
            "allergens": chosen["allergens"]
        }
    return None

def generate_weekly_grocery_list(meals: List[Dict[str, Any]], budget_tier: str = "Medium / Balanced") -> Dict[str, Any]:
    grains = set()
    proteins = set()
    produce = set()
    pantry = set()

    for m in meals:
        name = m["food_name"].lower()
        if any(w in name for w in ["roti", "phulka", "rice", "poha", "oats", "upma", "dalia", "idli", "dosa", "bhakri"]):
            grains.add("Whole Wheat Atta / Rolled Oats / Brown Rice / Poha")
        if any(w in name for w in ["dal", "rajma", "chole", "moong", "chana", "sattu"]):
            proteins.add("Yellow Moong Dal / Toor Dal / Rajma / Chickpeas")
        if "paneer" in name:
            proteins.add("Fresh Low-Fat Paneer (approx. 500g)")
        if "tofu" in name or "soya" in name:
            proteins.add("Firm Tofu / Soya Chunks (approx. 400g)")
        if "egg" in name:
            proteins.add("Eggs (1-2 dozen)")
        if "chicken" in name:
            proteins.add("Skinless Chicken Breast / Curry Cut (1 kg)")
        if "fish" in name:
            proteins.add("Fresh Rohu / Surmai / White Fish (500g)")
        if any(w in name for w in ["palak", "bhindi", "lauki", "gobi", "cabbage", "beans", "tindora", "vegetable"]):
            produce.add("Seasonal Greens (Spinach, Bottle Gourd, Okra, French Beans, Tomatoes, Cucumbers)")
        if any(w in name for w in ["papaya", "apple", "fruit", "lemon", "coconut"]):
            produce.add("Fresh Seasonal Fruits & Lemons (Papaya, Apples, Guava, Tender Coconut)")
        if any(w in name for w in ["almond", "walnut", "makhana", "chia", "flax", "peanuts"]):
            pantry.add("Seeds & Nuts (Almonds, Chia seeds, Foxnuts / Makhana, Peanuts)")
        if any(w in name for w in ["curd", "buttermilk", "chaas", "milk"]):
            proteins.add("Low-fat Fresh Curd & Milk / Plant Milk")

    if "low" in budget_tier.lower():
        estimated_budget_inr = "₹700 – ₹1,000 / week (Focus on wholesome lentils, seasonal sabzi, and whole grains)"
    elif "flexible" in budget_tier.lower():
        estimated_budget_inr = "₹1,800 – ₹2,500 / week (Includes imported nuts, berries, lean cuts, and organic staples)"
    else:
        estimated_budget_inr = "₹1,100 – ₹1,600 / week (Balanced mix of fresh dairy/plant proteins, seasonal vegetables, and nuts)"

    return {
        "Grains & Millets": sorted(list(grains)),
        "Proteins & Dairy / Alternatives": sorted(list(proteins)),
        "Fresh Vegetables & Fruits": sorted(list(produce)),
        "Nuts, Seeds & Healthy Fats": sorted(list(pantry)),
        "Estimated Weekly Grocery Cost": estimated_budget_inr
    }
