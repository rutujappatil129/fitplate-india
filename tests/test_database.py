import unittest
import sys
import os
import gc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db = str(Path(__file__).resolve().parent / "test_db_crud.db")
        database.init_db(self.test_db)

    def tearDown(self):
        gc.collect()
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except OSError:
                pass

    def test_user_and_profile_crud(self):
        uid = database.create_user("raj@domain.com", "hash123", "salt123", "Raj Malhotra", db_path=self.test_db)
        self.assertIsNotNone(uid)

        user = database.get_user_by_id(uid, db_path=self.test_db)
        self.assertEqual(user["full_name"], "Raj Malhotra")

        # Upsert profile
        profile_data = {
            "age": 30,
            "sex": "Male",
            "gender_identity": "Cisgender",
            "height_cm": 178.0,
            "current_weight_kg": 82.0,
            "target_weight_kg": 75.0,
            "goal": "Lose Weight",
            "activity_level": "Moderately Active",
            "diet_type": "Vegetarian",
            "regional_cuisine": "North Indian",
            "allergies": "None",
            "intolerances": "",
            "liked_foods": "Paneer, Dal",
            "disliked_foods": "Bitter gourd",
            "religious_restrictions": "",
            "medical_conditions": "None",
            "is_pregnant_or_lactating": False,
            "injuries_or_limitations": "None",
            "food_budget": "Medium / Balanced",
            "meals_per_day": 5,
            "preferred_meal_times": "8am, 1pm, 8pm",
            "sleep_duration_hours": 7.5,
            "exercise_experience": "Intermediate",
            "available_exercise_time_min": 45,
            "equipment": "Dumbbells"
        }
        database.upsert_user_profile(uid, profile_data, db_path=self.test_db)
        prof = database.get_user_profile(uid, db_path=self.test_db)
        self.assertEqual(prof["age"], 30)
        self.assertEqual(prof["goal"], "Lose Weight")

    def test_diet_plan_persistence_and_meal_swap(self):
        uid = database.create_user("anita@domain.com", "hash", "salt", "Anita Roy", db_path=self.test_db)
        meals = [{
            "day_of_week": "Monday",
            "meal_slot": "Breakfast",
            "food_name": "Vegetable Poha",
            "portion_unit": "1 bowl",
            "portion_size_g": 180,
            "calories": 260.0,
            "protein_g": 5.5,
            "carbs_g": 44.0,
            "fat_g": 7.5,
            "fiber_g": 3.8,
            "prep_notes": "Sauté with peas",
            "substitutions": "Upma",
            "allergens": "Peanuts",
            "is_completed": False
        }]
        plan_id = database.save_diet_plan(uid, "2026-10-18", 1800, 70, 240, 50, meals, db_path=self.test_db)
        self.assertIsNotNone(plan_id)

        plan, saved_meals = database.get_latest_diet_plan(uid, db_path=self.test_db)
        self.assertEqual(len(saved_meals), 1)
        self.assertEqual(saved_meals[0]["food_name"], "Vegetable Poha")

        # Mark meal complete
        database.update_meal_completion(saved_meals[0]["id"], True, db_path=self.test_db)
        _, updated_meals = database.get_latest_diet_plan(uid, db_path=self.test_db)
        self.assertTrue(updated_meals[0]["is_completed"])

    def test_cascade_delete_user(self):
        uid = database.create_user("delete_me@domain.com", "h", "s", "Test Delete", db_path=self.test_db)
        database.add_weight_log(uid, "2026-10-18", 75.0, db_path=self.test_db)
        self.assertEqual(len(database.get_weight_logs(uid, db_path=self.test_db)), 1)

        # Delete user
        deleted = database.delete_user_account(uid, db_path=self.test_db)
        self.assertTrue(deleted)

        # Logs must cascade delete
        self.assertEqual(len(database.get_weight_logs(uid, db_path=self.test_db)), 0)

if __name__ == "__main__":
    unittest.main()
