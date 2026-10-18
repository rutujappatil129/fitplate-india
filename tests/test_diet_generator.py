import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services import diet_generator

class TestDietGenerator(unittest.TestCase):
    def setUp(self):
        self.all_foods = diet_generator.load_foods_database()

    def test_load_foods_database(self):
        self.assertGreater(len(self.all_foods), 20)
        sample = self.all_foods[0]
        self.assertIn("name", sample)
        self.assertIn("calories", sample)
        self.assertIn("protein_g", sample)

    def test_vegan_diet_filtering(self):
        profile = {
            "diet_type": "Vegan",
            "allergies": "",
            "disliked_foods": ""
        }
        filtered = diet_generator.filter_foods_for_user(self.all_foods, profile)
        for food in filtered:
            self.assertTrue(food["is_vegan_safe"], f"{food['name']} is marked safe for vegan but is_vegan_safe is False")
            self.assertNotIn("dairy", food["allergens"].lower())
            self.assertNotIn("egg", food["diet_type"].lower())
            self.assertNotEqual(food["diet_type"], "Non-Vegetarian")

    def test_jain_vegetarian_filtering(self):
        profile = {
            "diet_type": "Jain Vegetarian",
            "allergies": "",
            "disliked_foods": ""
        }
        filtered = diet_generator.filter_foods_for_user(self.all_foods, profile)
        self.assertGreater(len(filtered), 5)
        for food in filtered:
            self.assertTrue(food["is_jain_safe"], f"{food['name']} must be Jain-safe")
            self.assertNotEqual(food["diet_type"], "Non-Vegetarian")
            self.assertNotEqual(food["diet_type"], "Eggetarian")

    def test_allergy_filtering(self):
        profile = {
            "diet_type": "Vegetarian",
            "allergies": "Peanuts / Tree Nuts, Dairy / Lactose",
            "disliked_foods": ""
        }
        filtered = diet_generator.filter_foods_for_user(self.all_foods, profile)
        for food in filtered:
            self.assertNotIn("dairy", food["allergens"].lower())
            self.assertNotIn("nut", food["allergens"].lower())

    def test_seven_day_plan_generation(self):
        profile = {
            "diet_type": "Vegetarian",
            "allergies": "",
            "disliked_foods": "",
            "regional_cuisine": "North Indian",
            "meals_per_day": 5
        }
        target_calories = 1800.0
        meals, summary = diet_generator.generate_seven_day_diet_plan(profile, target_calories)
        
        # 7 days x 5 meals = 35 meals
        self.assertEqual(len(meals), 35)
        self.assertGreater(summary["daily_avg_calories"], 1000)
        self.assertGreater(summary["daily_avg_protein"], 30)

        # Days verification
        days_in_plan = {m["day_of_week"] for m in meals}
        self.assertEqual(len(days_in_plan), 7)

    def test_weekly_grocery_list_generator(self):
        profile = {
            "diet_type": "Vegetarian",
            "allergies": "",
            "disliked_foods": "",
            "meals_per_day": 4
        }
        meals, _ = diet_generator.generate_seven_day_diet_plan(profile, 2000.0)
        groceries = diet_generator.generate_weekly_grocery_list(meals, budget_tier="Medium / Balanced")
        self.assertIn("Grains & Millets", groceries)
        self.assertIn("Proteins & Dairy / Alternatives", groceries)
        self.assertIn("Estimated Weekly Grocery Cost", groceries)

if __name__ == "__main__":
    unittest.main()
