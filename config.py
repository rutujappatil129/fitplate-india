"""
FitPlate India - System Configuration and Constants
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FOODS_CSV_PATH = DATA_DIR / "indian_foods.csv"
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "fitplate_india.db"))
IS_HOSTED = os.getenv("FITPLATE_HOSTED", "false").lower() == "true"

APP_TITLE = "FitPlate India"
APP_TAGLINE = "Personalized Indian Diet Planner & Health Analyzer"
APP_VERSION = "1.0.0"

# Caloric Densities
PROTEIN_KCAL_PER_G = 4.0
CARB_KCAL_PER_G = 4.0
FAT_KCAL_PER_G = 9.0

# Safety thresholds
MIN_SAFE_CALORIES_MALE = 1500
MIN_SAFE_CALORIES_FEMALE = 1200
MIN_SAFE_AGE = 18

DIET_TYPES = [
    "Vegetarian",
    "Eggetarian",
    "Non-Vegetarian",
    "Vegan",
    "Jain Vegetarian"
]

REGIONAL_CUISINES = [
    "Pan-Indian",
    "North Indian",
    "South Indian",
    "Maharashtrian",
    "Gujarati"
]

COMMON_ALLERGENS = [
    "Dairy / Lactose",
    "Gluten / Wheat",
    "Peanuts / Tree Nuts",
    "Soy",
    "Eggs",
    "Fish / Seafood"
]

MEAL_SLOTS = [
    "Early Morning",
    "Breakfast",
    "Mid-Morning Snack",
    "Lunch",
    "Evening Snack",
    "Dinner"
]

BUDGET_LEVELS = [
    "Low / Pocket-Friendly",
    "Medium / Balanced",
    "Flexible"
]

EQUIPMENT_OPTIONS = [
    "None (Bodyweight / Chair)",
    "Resistance Bands",
    "Dumbbells",
    "Full Gym"
]

FITNESS_LEVELS = [
    "Beginner",
    "Intermediate",
    "Advanced"
]

GOAL_OPTIONS = [
    "Lose Weight",
    "Maintain Weight",
    "Gain Weight / Muscle",
    "Improve General Fitness"
]

ACTIVITY_LEVELS = [
    "Sedentary (little to no exercise, desk job)",
    "Lightly Active (light exercise 1-3 days/week)",
    "Moderately Active (moderate exercise 3-5 days/week)",
    "Very Active (hard exercise 6-7 days/week)"
]

DISCLAIMER_TEXT = (
    "FitPlate India provides general wellness and educational estimates based on standard nutritional formulas "
    "(Mifflin-St Jeor equation & ICMR guidelines). It is not a medical diagnostic or individual therapeutic tool. "
    "Please consult a registered dietitian, physician, or certified health practitioner before initiating "
    "any drastic nutritional modification or exercise regimen, especially if you have diagnosed medical conditions."
)
