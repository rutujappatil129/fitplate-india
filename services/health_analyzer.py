from typing import Dict, Any, Tuple, Optional
import config

def calculate_bmi(weight_kg: float, height_cm: float) -> Tuple[float, str, str]:
    """
    Calculates BMI and returns (bmi_value, category, explanation).
    Uses Asian-Indian specific risk thresholds where overweight starts at 23.0 kg/m^2.
    """
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0, "Invalid Input", "Height and weight must be greater than zero."
    
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)
    
    # Asian-Indian BMI classification (ICMR / WHO consensus for South Asians)
    if bmi < 18.5:
        category = "Underweight"
        desc = "Your BMI is below the healthy range. Focusing on nutrient-dense meals and strength training can support healthy weight gain."
    elif 18.5 <= bmi <= 22.9:
        category = "Normal / Healthy Weight"
        desc = "Your BMI falls in the recommended healthy range for Asian adults."
    elif 23.0 <= bmi <= 24.9:
        category = "Overweight (Asian-Indian Threshold)"
        desc = "Your BMI is slightly elevated based on South Asian health thresholds, which note higher metabolic risk above 23."
    else:
        category = "Obesity"
        desc = "Your BMI indicates higher adiposity risk. Consistent lifestyle, balanced eating, and regular physical activity are beneficial."

    limitation_note = (
        "Note: BMI is a general screening indicator. It does not distinguish between muscle mass, "
        "bone density, and body fat distribution (such as abdominal fat)."
    )
    return bmi, category, f"{desc} {limitation_note}"

def calculate_bmr_mifflin_st_jeor(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """
    Calculates Basal Metabolic Rate using the Mifflin-St Jeor formula.
    Male: 10*W + 6.25*H - 5*A + 5
    Female: 10*W + 6.25*H - 5*A - 161
    """
    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
    if sex.strip().lower() == "female":
        return round(base - 161.0, 1)
    else:
        return round(base + 5.0, 1)

def get_activity_multiplier(activity_level_str: str) -> float:
    lvl = activity_level_str.lower()
    if "very active" in lvl:
        return 1.725
    elif "moderately active" in lvl:
        return 1.55
    elif "lightly active" in lvl:
        return 1.375
    else: # Sedentary
        return 1.2

def calculate_tdee(bmr: float, activity_level: str) -> float:
    multiplier = get_activity_multiplier(activity_level)
    return round(bmr * multiplier, 1)

def analyze_safety_flags(profile: Dict[str, Any]) -> Tuple[bool, list[str]]:
    """
    Evaluates profile for safety risks, medical conditions, and clinical flags.
    Returns (has_safety_block, list_of_warning_messages).
    """
    flags = []
    has_block = False
    
    age = profile.get("age", 25)
    goal = profile.get("goal", "Maintain Weight")
    med_conditions = profile.get("medical_conditions", "").lower()
    is_preg = profile.get("is_pregnant_or_lactating", False)
    weight = profile.get("current_weight_kg", 70.0)
    target = profile.get("target_weight_kg", 65.0)
    height_cm = profile.get("height_cm", 170.0)
    
    # 1. Age limitation
    if age < config.MIN_SAFE_AGE:
        flags.append(
            "Pediatric / Adolescent Safety Notice: Nutritional requirements for individuals under 18 differ "
            "greatly from adults. FitPlate India does not provide automated weight-loss targets for youth. "
            "Please consult a pediatrician or pediatric dietitian."
        )
        if "lose" in goal.lower():
            has_block = True

    # 2. Pregnancy & Lactation
    if is_preg:
        flags.append(
            "Pregnancy / Lactation Safety Flag: Energy and nutrient requirements are specialized during pregnancy "
            "and nursing. Automated calorie restriction is unsafe. Please work directly with your obstetrician and clinical dietitian."
        )
        if "lose" in goal.lower():
            has_block = True

    # 3. Eating Disorder history
    if "eating disorder" in med_conditions:
        flags.append(
            "Eating Disorder History Flag: Calorie counting and deficit tracking can be counter-therapeutic. "
            "We strongly suggest consulting an eating disorder specialist and focusing on intuitive, nourishing meals."
        )
        has_block = True

    # 4. Severe medical conditions
    if any(cond in med_conditions for cond in ["kidney", "renal", "heart disease", "cardiac"]):
        flags.append(
            "Clinical Oversight Required: You reported a condition (e.g. kidney or heart disease) that requires "
            "customized sodium, potassium, fluid, or protein titration. Follow your physician's clinical diet chart."
        )
        has_block = True

    # 5. Underweight attempting weight loss
    bmi = weight / ((height_cm / 100.0) ** 2)
    if bmi < 18.5 and "lose" in goal.lower():
        flags.append(
            "Underweight Safety Alert: Your current BMI is already below 18.5 kg/m². "
            "Further weight loss is medically contraindicated. Our recommendations will focus on nutrient density and maintenance."
        )
        has_block = True

    return has_block, flags

def generate_health_summary(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generates the complete health and energy analysis breakdown."""
    age = int(profile.get("age", 25))
    sex = profile.get("sex", "Male")
    height_cm = float(profile.get("height_cm", 170.0))
    current_weight_kg = float(profile.get("current_weight_kg", 70.0))
    target_weight_kg = float(profile.get("target_weight_kg", 65.0))
    activity_level = profile.get("activity_level", "Moderately Active")
    goal = profile.get("goal", "Lose Weight")
    
    bmi, bmi_category, bmi_desc = calculate_bmi(current_weight_kg, height_cm)
    bmr = calculate_bmr_mifflin_st_jeor(current_weight_kg, height_cm, age, sex)
    tdee = calculate_tdee(bmr, activity_level)
    
    has_safety_block, safety_warnings = analyze_safety_flags(profile)
    
    # Caloric adjustment with safety floors
    min_floor = config.MIN_SAFE_CALORIES_FEMALE if sex.lower() == "female" else config.MIN_SAFE_CALORIES_MALE
    
    if has_safety_block or "maintain" in goal.lower() or "general fitness" in goal.lower():
        target_calories = tdee
        calorie_adjustment_note = "Estimated maintenance intake based on your current physical activity level."
    elif "lose" in goal.lower():
        deficit = 400.0
        target_calories = max(tdee - deficit, min_floor)
        calorie_adjustment_note = f"Conservative deficit of ~400 kcal below TDEE (safeguarded by minimum safe floor of {min_floor} kcal)."
    elif "gain" in goal.lower():
        surplus = 350.0
        target_calories = tdee + surplus
        calorie_adjustment_note = "Gentle surplus of ~350 kcal above TDEE paired with resistance training for lean mass."
    else:
        target_calories = tdee
        calorie_adjustment_note = "Maintenance intake."

    target_calories = round(target_calories)

    # Macronutrient distribution
    # Protein: 1.2g to 1.6g per kg body weight depending on goal
    if "lose" in goal.lower():
        protein_g = round(current_weight_kg * 1.4)
    elif "gain" in goal.lower():
        protein_g = round(current_weight_kg * 1.6)
    else:
        protein_g = round(current_weight_kg * 1.1)

    protein_kcal = protein_g * config.PROTEIN_KCAL_PER_G
    fat_kcal = target_calories * 0.28
    fat_g = round(fat_kcal / config.FAT_KCAL_PER_G)
    
    carb_kcal = max(target_calories - (protein_kcal + fat_kcal), 300)
    carbs_g = round(carb_kcal / config.CARB_KCAL_PER_G)

    # Hydration estimate (35ml per kg body weight + 350ml if moderately/very active)
    hydration_ml = int(current_weight_kg * 35)
    if "moderate" in activity_level.lower() or "very" in activity_level.lower():
        hydration_ml += 350
    # Safe bounds: 2000ml to 3800ml
    hydration_ml = max(2000, min(hydration_ml, 3800))

    # Sleep guidance
    sleep_hours = profile.get("sleep_duration_hours", 7.5)
    if sleep_hours < 7.0:
        sleep_obs = f"You reported {sleep_hours} hrs of sleep. Aim for 7 to 9 hours of restorative sleep to assist hormonal recovery and appetite regulation."
    elif sleep_hours > 9.0:
        sleep_obs = f"You reported {sleep_hours} hrs of sleep. Ensure your sleep schedule is regular and energizing."
    else:
        sleep_obs = f"Your reported {sleep_hours} hrs of sleep is well within the healthy adult restorative range (7-9 hrs)."

    return {
        "bmi": bmi,
        "bmi_category": bmi_category,
        "bmi_description": bmi_desc,
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_calories,
        "calorie_adjustment_note": calorie_adjustment_note,
        "target_protein_g": protein_g,
        "target_carbs_g": carbs_g,
        "target_fat_g": fat_g,
        "hydration_ml": hydration_ml,
        "sleep_observation": sleep_obs,
        "has_safety_block": has_safety_block,
        "safety_warnings": safety_warnings
    }
