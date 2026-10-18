from typing import List, Dict, Any, Optional

def generate_seven_day_exercise_plan(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generates a personalized, safe 7-day exercise routine adapted to fitness level,
    time availability, available equipment, and physical injuries/limitations.
    """
    experience = profile.get("exercise_experience", "Beginner").capitalize()
    time_min = profile.get("available_exercise_time_min", 30)
    equipment = profile.get("equipment", "None (Bodyweight / Chair)")
    injuries = profile.get("injuries_or_limitations", "").lower()
    goal = profile.get("goal", "Lose Weight").lower()
    
    has_knee_issue = "knee" in injuries or "joint" in injuries
    has_back_issue = "back" in injuries or "spine" in injuries
    has_shoulder_issue = "shoulder" in injuries

    # Volume and sets based on experience
    if experience == "Advanced":
        sets_reps = f"4 sets x 12-15 reps ({time_min} mins total)"
        rest_sec = "45-60 seconds between sets"
        diff = "Advanced"
    elif experience == "Intermediate":
        sets_reps = f"3 sets x 10-12 reps ({time_min} mins total)"
        rest_sec = "60-75 seconds between sets"
        diff = "Intermediate"
    else: # Beginner
        sets_reps = f"2-3 sets x 8-10 reps ({time_min} mins total)"
        rest_sec = "75-90 seconds between sets"
        diff = "Beginner"

    # Base routine across 7 days
    days_structure = [
        {
            "day": "Monday",
            "title": "Full-Body Strength & Mobility",
            "default_exercise": "Wall Push-ups & Bodyweight Squats",
            "knee_alt": "Wall Push-ups & Glute Bridges (Knee-Friendly)",
            "back_alt": "Elevated Wall Push-ups & Supported Chair Squats",
            "mod": "Perform against a wall or sturdy table; reduce knee bending depth",
            "safety": "Keep core engaged, do not hold your breath, exhale as you push"
        },
        {
            "day": "Tuesday",
            "title": "Low-Impact Cardio & Posture Work",
            "default_exercise": "Brisk Walking & Arm Reaches",
            "knee_alt": "Gentle Flat Surface Walking or Seated Marching",
            "back_alt": "Upright Walking with Posture Realignment",
            "mod": "Pace yourself at a conversational speed (RPE 5-6 out of 10)",
            "safety": "Wear supportive athletic footwear; maintain upright gaze"
        },
        {
            "day": "Wednesday",
            "title": "Lower Body & Core Stability",
            "default_exercise": "Chair Squats & Bird-Dog Plank Holds",
            "knee_alt": "Supine Glute Bridges & Seated Straight Leg Raises",
            "back_alt": "Dead Bug & Gentle Pelvic Tilts (Back-Safe)",
            "mod": "Keep chair directly behind you as a physical safety touchpoint",
            "safety": "Keep your knees pointing in line with second toe; avoid caving inward"
        },
        {
            "day": "Thursday",
            "title": "Gentle Yoga Flow & Active Rest",
            "default_exercise": "Cat-Cow Stretch, Child's Pose & Gentle Hamstring Stretch",
            "knee_alt": "Seated Cat-Cow & Seated Forward Fold (No Knee Kneeling)",
            "back_alt": "Neutral Spine Breathing & Gentle Reclined Knee-to-Chest",
            "mod": "Use cushions/yoga blocks under knees for gentle joint padding",
            "safety": "Move smoothly through comfortable ranges of motion without sharp pain"
        },
        {
            "day": "Friday",
            "title": "Upper Body Strength & Postural Health",
            "default_exercise": "Incline Push-ups & Seated Resistance Row",
            "knee_alt": "Seated Incline Row & Chest Flyes",
            "back_alt": "Chest-Supported Dumbbell/Band Rows (Neutral Spine)",
            "mod": "Use a light resistance band or 1-2 liter water bottles if dumbbells are unavailable",
            "safety": "Pull shoulder blades down and back; avoid shrugging ears"
        },
        {
            "day": "Saturday",
            "title": "Enjoyable Movement / Moderate Aerobics",
            "default_exercise": "Outdoor Brisk Walk, Dance Movement or Cycling",
            "knee_alt": "Stationary Cycling (low resistance) or Gentle Swimming",
            "back_alt": "Smooth Walking with Arm Swings on Soft Track",
            "mod": "Break into two 15-minute intervals if 30 minutes feels tiring",
            "safety": "Stay well-hydrated before and after session"
        },
        {
            "day": "Sunday",
            "title": "Complete Rest, Deep Breathing & Recovery",
            "default_exercise": "Full Body Relaxation & Gentle Walking (15 min)",
            "knee_alt": "Elevate Legs & Gentle Ankle Pumps",
            "back_alt": "Diaphragmatic Belly Breathing in Savasana",
            "mod": "No strenuous exertion; allow muscles and nervous system to rejuvenate",
            "safety": "Prioritize 8 hours of restorative sleep and gentle hydration"
        }
    ]

    plan_items = []
    for d in days_structure:
        # Determine appropriate exercise taking injuries into account
        if has_knee_issue:
            ex_name = d["knee_alt"]
        elif has_back_issue:
            ex_name = d["back_alt"]
        else:
            ex_name = d["default_exercise"]

        plan_items.append({
            "day_of_week": d["day"],
            "session_title": d["title"],
            "exercise_name": ex_name,
            "duration_or_reps": sets_reps if "Rest" not in d["title"] else f"15-20 mins ({diff})",
            "equipment_needed": equipment,
            "difficulty": diff,
            "beginner_modification": d["mod"],
            "rest_period": rest_sec,
            "warmup": "5 min dynamic joint rotations (arm circles, torso twists, ankle pumps)",
            "cooldown": "5 min static stretching (quad stretch, chest opener, deep breaths)",
            "safety_instructions": d["safety"],
            "is_completed": False
        })

    return plan_items
