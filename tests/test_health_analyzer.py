import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services import health_analyzer

class TestHealthAnalyzer(unittest.TestCase):
    def test_calculate_bmi(self):
        # Normal weight: 65kg, 172cm -> 22.0
        bmi, cat, desc = health_analyzer.calculate_bmi(65.0, 172.0)
        self.assertEqual(bmi, 22.0)
        self.assertIn("Normal", cat)

        # Asian-Indian Overweight threshold: 72kg, 172cm -> 24.3
        bmi2, cat2, _ = health_analyzer.calculate_bmi(72.0, 172.0)
        self.assertEqual(bmi2, 24.3)
        self.assertIn("Overweight", cat2)

        # Underweight: 45kg, 165cm -> 16.5
        bmi3, cat3, _ = health_analyzer.calculate_bmi(45.0, 165.0)
        self.assertEqual(bmi3, 16.5)
        self.assertIn("Underweight", cat3)

    def test_bmr_mifflin_st_jeor(self):
        # Male: 10*70 + 6.25*175 - 5*25 + 5 = 700 + 1093.75 - 125 + 5 = 1673.75 -> 1673.8
        bmr_m = health_analyzer.calculate_bmr_mifflin_st_jeor(70.0, 175.0, 25, "Male")
        self.assertAlmostEqual(bmr_m, 1673.8, delta=0.5)

        # Female: 10*60 + 6.25*160 - 5*30 - 161 = 600 + 1000 - 150 - 161 = 1289.0
        bmr_f = health_analyzer.calculate_bmr_mifflin_st_jeor(60.0, 160.0, 30, "Female")
        self.assertAlmostEqual(bmr_f, 1289.0, delta=0.5)

    def test_pediatric_safety_flag(self):
        # User under 18 seeking weight loss must trigger pediatric block
        profile = {
            "age": 16,
            "sex": "Female",
            "height_cm": 155.0,
            "current_weight_kg": 58.0,
            "target_weight_kg": 50.0,
            "goal": "Lose Weight",
            "activity_level": "Sedentary"
        }
        res = health_analyzer.generate_health_summary(profile)
        self.assertTrue(res["has_safety_block"])
        self.assertTrue(any("Pediatric" in w for w in res["safety_warnings"]))

    def test_pregnancy_safety_flag(self):
        profile = {
            "age": 28,
            "sex": "Female",
            "height_cm": 162.0,
            "current_weight_kg": 68.0,
            "target_weight_kg": 60.0,
            "goal": "Lose Weight",
            "is_pregnant_or_lactating": True,
            "activity_level": "Lightly Active"
        }
        res = health_analyzer.generate_health_summary(profile)
        self.assertTrue(res["has_safety_block"])
        self.assertTrue(any("Pregnancy" in w for w in res["safety_warnings"]))

    def test_kidney_disease_flag(self):
        profile = {
            "age": 45,
            "sex": "Male",
            "height_cm": 170.0,
            "current_weight_kg": 75.0,
            "target_weight_kg": 70.0,
            "medical_conditions": "Chronic Kidney Disease Stage 2",
            "goal": "Lose Weight"
        }
        res = health_analyzer.generate_health_summary(profile)
        self.assertTrue(res["has_safety_block"])
        self.assertTrue(any("Kidney" in w or "Clinical" in w for w in res["safety_warnings"]))

if __name__ == "__main__":
    unittest.main()
