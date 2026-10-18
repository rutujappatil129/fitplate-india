from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

@dataclass
class User:
    id: Optional[int] = None
    email: str = ""
    password_hash: str = ""
    salt: str = ""
    full_name: str = ""
    created_at: str = ""

@dataclass
class UserProfile:
    id: Optional[int] = None
    user_id: int = 0
    age: int = 25
    sex: str = "Male"                  # For MSJ BMR formula: "Male" or "Female"
    gender_identity: str = ""          # Optional respectful personalization
    height_cm: float = 170.0
    current_weight_kg: float = 70.0
    target_weight_kg: float = 65.0
    goal: str = "Lose Weight"
    activity_level: str = "Moderately Active (moderate exercise 3-5 days/week)"
    diet_type: str = "Vegetarian"
    regional_cuisine: str = "Pan-Indian"
    allergies: str = ""                # comma-separated
    intolerances: str = ""
    liked_foods: str = ""
    disliked_foods: str = ""
    religious_restrictions: str = ""
    medical_conditions: str = ""       # e.g., "None", "Diabetes", "Kidney", "Eating Disorder"
    is_pregnant_or_lactating: bool = False
    injuries_or_limitations: str = ""  # e.g., "Knee pain", "Lower back stiffness"
    food_budget: str = "Medium / Balanced"
    meals_per_day: int = 5
    preferred_meal_times: str = ""
    sleep_duration_hours: float = 7.5
    exercise_experience: str = "Beginner"
    available_exercise_time_min: int = 30
    equipment: str = "None (Bodyweight / Chair)"
    updated_at: str = ""

@dataclass
class DietPlanMeal:
    id: Optional[int] = None
    plan_id: int = 0
    day_of_week: str = "Monday"
    meal_slot: str = "Breakfast"
    food_name: str = ""
    portion_unit: str = ""
    portion_size_g: float = 0.0
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    fiber_g: float = 0.0
    prep_notes: str = ""
    substitutions: str = ""
    allergens: str = "None"
    is_completed: bool = False

@dataclass
class DietPlan:
    id: Optional[int] = None
    user_id: int = 0
    week_start_date: str = ""
    target_calories_daily: float = 2000.0
    target_protein_g: float = 75.0
    target_carbs_g: float = 250.0
    target_fat_g: float = 55.0
    meals: List[DietPlanMeal] = field(default_factory=list)
    created_at: str = ""

@dataclass
class ExerciseItem:
    id: Optional[int] = None
    plan_id: int = 0
    day_of_week: str = "Monday"
    session_title: str = "Full Body Mobility & Strength"
    exercise_name: str = "Chair Squats"
    duration_or_reps: str = "3 sets x 10 reps"
    equipment_needed: str = "Sturdy chair"
    difficulty: str = "Beginner"
    beginner_modification: str = "Sit down fully and stand up with arm support"
    rest_period: str = "60-90 sec rest between sets"
    warmup: str = "5 min brisk arm circles and shoulder rolls"
    cooldown: str = "5 min gentle hamstring and chest stretch"
    safety_instructions: str = "Keep knees tracking over toes; avoid rounding lower back"
    is_completed: bool = False

@dataclass
class WeightLog:
    id: Optional[int] = None
    user_id: int = 0
    log_date: str = ""
    weight_kg: float = 0.0
    waist_cm: Optional[float] = None
    notes: str = ""
    created_at: str = ""

@dataclass
class HydrationLog:
    id: Optional[int] = None
    user_id: int = 0
    log_date: str = ""
    amount_ml: int = 0
    created_at: str = ""

@dataclass
class DailyHabitLog:
    id: Optional[int] = None
    user_id: int = 0
    log_date: str = ""
    sleep_hours: float = 0.0
    exercise_completed: bool = False
    diet_followed: bool = False
    fruits_veggies_consumed: bool = False
    daily_steps: int = 0
    mood_rating: int = 5
    notes: str = ""
    created_at: str = ""
