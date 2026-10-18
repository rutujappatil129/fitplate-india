import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services import exercise_generator

class TestExerciseGenerator(unittest.TestCase):
    def test_seven_day_plan_structure(self):
        profile = {
            "exercise_experience": "Intermediate",
            "available_exercise_time_min": 40,
            "equipment": "Dumbbells",
            "injuries_or_limitations": ""
        }
        items = exercise_generator.generate_seven_day_exercise_plan(profile)
        self.assertEqual(len(items), 7)
        self.assertEqual(items[0]["difficulty"], "Intermediate")
        self.assertEqual(items[0]["day_of_week"], "Monday")
        self.assertEqual(items[-1]["day_of_week"], "Sunday")
        self.assertIn("Dumbbells", items[0]["equipment_needed"])

    def test_knee_injury_adaptation(self):
        profile = {
            "exercise_experience": "Beginner",
            "available_exercise_time_min": 30,
            "equipment": "None (Bodyweight / Chair)",
            "injuries_or_limitations": "Mild knee osteoarthritis"
        }
        items = exercise_generator.generate_seven_day_exercise_plan(profile)
        # Monday or Wednesday exercise should specify Knee-Friendly / glute bridge / leg raises
        ex_names = [it["exercise_name"] for it in items]
        has_knee_mod = any("Knee" in name or "Glute" in name for name in ex_names)
        self.assertTrue(has_knee_mod, "Knee modification was not adapted in exercise plan")

    def test_back_injury_adaptation(self):
        profile = {
            "exercise_experience": "Beginner",
            "available_exercise_time_min": 20,
            "equipment": "None",
            "injuries_or_limitations": "Lower back pain"
        }
        items = exercise_generator.generate_seven_day_exercise_plan(profile)
        ex_names = [it["exercise_name"] for it in items]
        has_back_mod = any("Back" in name or "Pelvic" in name or "Dead Bug" in name for name in ex_names)
        self.assertTrue(has_back_mod, "Back modification was not adapted in exercise plan")

if __name__ == "__main__":
    unittest.main()
