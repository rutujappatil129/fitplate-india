import sqlite3
import os
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from pathlib import Path
from config import DB_PATH

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def db_session(db_path: Optional[str] = None):
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db(db_path: Optional[str] = None):
    """Initializes the database tables and indexes."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        
        # 1. Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")

        # 2. User Profiles table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            age INTEGER NOT NULL DEFAULT 25,
            sex TEXT NOT NULL DEFAULT 'Male',
            gender_identity TEXT DEFAULT '',
            height_cm REAL NOT NULL DEFAULT 170.0,
            current_weight_kg REAL NOT NULL DEFAULT 70.0,
            target_weight_kg REAL NOT NULL DEFAULT 65.0,
            goal TEXT NOT NULL DEFAULT 'Lose Weight',
            activity_level TEXT NOT NULL DEFAULT 'Moderately Active',
            diet_type TEXT NOT NULL DEFAULT 'Vegetarian',
            regional_cuisine TEXT NOT NULL DEFAULT 'Pan-Indian',
            allergies TEXT DEFAULT '',
            intolerances TEXT DEFAULT '',
            liked_foods TEXT DEFAULT '',
            disliked_foods TEXT DEFAULT '',
            religious_restrictions TEXT DEFAULT '',
            medical_conditions TEXT DEFAULT '',
            is_pregnant_or_lactating BOOLEAN DEFAULT 0,
            injuries_or_limitations TEXT DEFAULT '',
            food_budget TEXT DEFAULT 'Medium / Balanced',
            meals_per_day INTEGER DEFAULT 5,
            preferred_meal_times TEXT DEFAULT '',
            sleep_duration_hours REAL DEFAULT 7.5,
            exercise_experience TEXT DEFAULT 'Beginner',
            available_exercise_time_min INTEGER DEFAULT 30,
            equipment TEXT DEFAULT 'None (Bodyweight / Chair)',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_profiles_uid ON user_profiles(user_id);")

        # 3. Diet Plans table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS diet_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            week_start_date TEXT NOT NULL,
            target_calories_daily REAL NOT NULL,
            target_protein_g REAL NOT NULL,
            target_carbs_g REAL NOT NULL,
            target_fat_g REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_diet_plans_uid ON diet_plans(user_id);")

        # 4. Diet Plan Meals table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS diet_plan_meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL,
            day_of_week TEXT NOT NULL,
            meal_slot TEXT NOT NULL,
            food_name TEXT NOT NULL,
            portion_unit TEXT NOT NULL,
            portion_size_g REAL NOT NULL,
            calories REAL NOT NULL,
            protein_g REAL NOT NULL,
            carbs_g REAL NOT NULL,
            fat_g REAL NOT NULL,
            fiber_g REAL NOT NULL,
            prep_notes TEXT,
            substitutions TEXT,
            allergens TEXT,
            is_completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (plan_id) REFERENCES diet_plans(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_diet_meals_plan ON diet_plan_meals(plan_id);")

        # 5. Exercise Plans table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercise_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_exercise_plans_uid ON exercise_plans(user_id);")

        # 6. Exercise Plan Items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercise_plan_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL,
            day_of_week TEXT NOT NULL,
            session_title TEXT NOT NULL,
            exercise_name TEXT NOT NULL,
            duration_or_reps TEXT NOT NULL,
            equipment_needed TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            beginner_modification TEXT,
            rest_period TEXT,
            warmup TEXT,
            cooldown TEXT,
            safety_instructions TEXT,
            is_completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (plan_id) REFERENCES exercise_plans(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_exercise_items_plan ON exercise_plan_items(plan_id);")

        # 7. Weight Logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            weight_kg REAL NOT NULL,
            waist_cm REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_weight_logs_uid_date ON weight_logs(user_id, log_date);")

        # 8. Hydration Logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hydration_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            amount_ml INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hydration_logs_uid_date ON hydration_logs(user_id, log_date);")

        # 9. Daily Habit Logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            sleep_hours REAL DEFAULT 0.0,
            exercise_completed BOOLEAN DEFAULT 0,
            diet_followed BOOLEAN DEFAULT 0,
            fruits_veggies_consumed BOOLEAN DEFAULT 0,
            daily_steps INTEGER DEFAULT 0,
            mood_rating INTEGER DEFAULT 5,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, log_date)
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_habit_logs_uid_date ON daily_habit_logs(user_id, log_date);")

# --- User Operations ---
def create_user(email: str, password_hash: str, salt: str, full_name: str, db_path: Optional[str] = None) -> Optional[int]:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (email, password_hash, salt, full_name) VALUES (?, ?, ?, ?)",
                (email.strip().lower(), password_hash, salt, full_name.strip())
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

def get_user_by_email(email: str, db_path: Optional[str] = None) -> Optional[sqlite3.Row]:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
        return cursor.fetchone()

def get_user_by_id(user_id: int, db_path: Optional[str] = None) -> Optional[sqlite3.Row]:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

def delete_user_account(user_id: int, db_path: Optional[str] = None) -> bool:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cursor.rowcount > 0

# --- Profile Operations ---
def upsert_user_profile(user_id: int, profile_data: Dict[str, Any], db_path: Optional[str] = None) -> bool:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO user_profiles (
            user_id, age, sex, gender_identity, height_cm, current_weight_kg,
            target_weight_kg, goal, activity_level, diet_type, regional_cuisine,
            allergies, intolerances, liked_foods, disliked_foods, religious_restrictions,
            medical_conditions, is_pregnant_or_lactating, injuries_or_limitations,
            food_budget, meals_per_day, preferred_meal_times, sleep_duration_hours,
            exercise_experience, available_exercise_time_min, equipment, updated_at
        ) VALUES (
            :user_id, :age, :sex, :gender_identity, :height_cm, :current_weight_kg,
            :target_weight_kg, :goal, :activity_level, :diet_type, :regional_cuisine,
            :allergies, :intolerances, :liked_foods, :disliked_foods, :religious_restrictions,
            :medical_conditions, :is_pregnant_or_lactating, :injuries_or_limitations,
            :food_budget, :meals_per_day, :preferred_meal_times, :sleep_duration_hours,
            :exercise_experience, :available_exercise_time_min, :equipment, CURRENT_TIMESTAMP
        )
        ON CONFLICT(user_id) DO UPDATE SET
            age = excluded.age,
            sex = excluded.sex,
            gender_identity = excluded.gender_identity,
            height_cm = excluded.height_cm,
            current_weight_kg = excluded.current_weight_kg,
            target_weight_kg = excluded.target_weight_kg,
            goal = excluded.goal,
            activity_level = excluded.activity_level,
            diet_type = excluded.diet_type,
            regional_cuisine = excluded.regional_cuisine,
            allergies = excluded.allergies,
            intolerances = excluded.intolerances,
            liked_foods = excluded.liked_foods,
            disliked_foods = excluded.disliked_foods,
            religious_restrictions = excluded.religious_restrictions,
            medical_conditions = excluded.medical_conditions,
            is_pregnant_or_lactating = excluded.is_pregnant_or_lactating,
            injuries_or_limitations = excluded.injuries_or_limitations,
            food_budget = excluded.food_budget,
            meals_per_day = excluded.meals_per_day,
            preferred_meal_times = excluded.preferred_meal_times,
            sleep_duration_hours = excluded.sleep_duration_hours,
            exercise_experience = excluded.exercise_experience,
            available_exercise_time_min = excluded.available_exercise_time_min,
            equipment = excluded.equipment,
            updated_at = CURRENT_TIMESTAMP;
        """, {**profile_data, "user_id": user_id})
        return True

def get_user_profile(user_id: int, db_path: Optional[str] = None) -> Optional[sqlite3.Row]:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        return cursor.fetchone()

# --- Diet Plan Operations ---
def save_diet_plan(user_id: int, week_start: str, calories: float, protein: float, carbs: float, fat: float, meals: List[Dict[str, Any]], db_path: Optional[str] = None) -> int:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM diet_plans WHERE user_id = ?", (user_id,))
        cursor.execute("""
            INSERT INTO diet_plans (user_id, week_start_date, target_calories_daily, target_protein_g, target_carbs_g, target_fat_g)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, week_start, calories, protein, carbs, fat))
        plan_id = cursor.lastrowid
        
        for m in meals:
            cursor.execute("""
                INSERT INTO diet_plan_meals (
                    plan_id, day_of_week, meal_slot, food_name, portion_unit,
                    portion_size_g, calories, protein_g, carbs_g, fat_g, fiber_g,
                    prep_notes, substitutions, allergens, is_completed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan_id, m["day_of_week"], m["meal_slot"], m["food_name"], m.get("portion_unit", "1 serving"),
                m.get("portion_size_g", 150), m["calories"], m["protein_g"], m["carbs_g"], m["fat_g"],
                m.get("fiber_g", 0.0), m.get("prep_notes", ""), m.get("substitutions", ""),
                m.get("allergens", "None"), m.get("is_completed", False)
            ))
        return plan_id

def get_latest_diet_plan(user_id: int, db_path: Optional[str] = None) -> Optional[Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM diet_plans WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
        plan_row = cursor.fetchone()
        if not plan_row:
            return None
        plan = dict(plan_row)
        cursor.execute("SELECT * FROM diet_plan_meals WHERE plan_id = ? ORDER BY id ASC", (plan["id"],))
        meals = [dict(m) for m in cursor.fetchall()]
        return plan, meals

def update_meal_completion(meal_id: int, is_completed: bool, db_path: Optional[str] = None) -> bool:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE diet_plan_meals SET is_completed = ? WHERE id = ?", (is_completed, meal_id))
        return cursor.rowcount > 0

def replace_plan_meal(meal_id: int, new_food_data: Dict[str, Any], db_path: Optional[str] = None) -> bool:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE diet_plan_meals
            SET food_name = ?, portion_unit = ?, portion_size_g = ?, calories = ?,
                protein_g = ?, carbs_g = ?, fat_g = ?, fiber_g = ?, prep_notes = ?,
                substitutions = ?, allergens = ?, is_completed = 0
            WHERE id = ?
        """, (
            new_food_data["food_name"], new_food_data.get("portion_unit", "1 serving"),
            new_food_data.get("portion_size_g", 150), new_food_data["calories"],
            new_food_data["protein_g"], new_food_data["carbs_g"], new_food_data["fat_g"],
            new_food_data.get("fiber_g", 0.0), new_food_data.get("prep_notes", ""),
            new_food_data.get("substitutions", ""), new_food_data.get("allergens", "None"),
            meal_id
        ))
        return cursor.rowcount > 0

# --- Exercise Plan Operations ---
def save_exercise_plan(user_id: int, items: List[Dict[str, Any]], db_path: Optional[str] = None) -> int:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM exercise_plans WHERE user_id = ?", (user_id,))
        cursor.execute("INSERT INTO exercise_plans (user_id) VALUES (?)", (user_id,))
        plan_id = cursor.lastrowid
        for it in items:
            cursor.execute("""
                INSERT INTO exercise_plan_items (
                    plan_id, day_of_week, session_title, exercise_name, duration_or_reps,
                    equipment_needed, difficulty, beginner_modification, rest_period,
                    warmup, cooldown, safety_instructions, is_completed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan_id, it["day_of_week"], it["session_title"], it["exercise_name"],
                it["duration_or_reps"], it.get("equipment_needed", "None"),
                it.get("difficulty", "Beginner"), it.get("beginner_modification", ""),
                it.get("rest_period", "60 sec"), it.get("warmup", ""), it.get("cooldown", ""),
                it.get("safety_instructions", ""), it.get("is_completed", False)
            ))
        return plan_id

def get_latest_exercise_plan(user_id: int, db_path: Optional[str] = None) -> Optional[Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM exercise_plans WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
        plan_row = cursor.fetchone()
        if not plan_row:
            return None
        plan = dict(plan_row)
        cursor.execute("SELECT * FROM exercise_plan_items WHERE plan_id = ? ORDER BY id ASC", (plan["id"],))
        items = [dict(it) for it in cursor.fetchall()]
        return plan, items

def update_exercise_item_completion(item_id: int, is_completed: bool, db_path: Optional[str] = None) -> bool:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE exercise_plan_items SET is_completed = ? WHERE id = ?", (is_completed, item_id))
        return cursor.rowcount > 0

# --- Weight Logs Operations ---
def add_weight_log(user_id: int, log_date: str, weight_kg: float, waist_cm: Optional[float] = None, notes: str = "", db_path: Optional[str] = None) -> int:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO weight_logs (user_id, log_date, weight_kg, waist_cm, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, log_date, weight_kg, waist_cm, notes))
        return cursor.lastrowid

def get_weight_logs(user_id: int, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM weight_logs WHERE user_id = ? ORDER BY log_date ASC, id ASC", (user_id,))
        return [dict(r) for r in cursor.fetchall()]

def delete_weight_log(log_id: int, user_id: int, db_path: Optional[str] = None) -> bool:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM weight_logs WHERE id = ? AND user_id = ?", (log_id, user_id))
        return cursor.rowcount > 0

# --- Hydration Operations ---
def add_hydration_log(user_id: int, log_date: str, amount_ml: int, db_path: Optional[str] = None) -> int:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hydration_logs (user_id, log_date, amount_ml)
            VALUES (?, ?, ?)
        """, (user_id, log_date, amount_ml))
        return cursor.lastrowid

def get_total_hydration_for_date(user_id: int, log_date: str, db_path: Optional[str] = None) -> int:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(amount_ml), 0) as total FROM hydration_logs
            WHERE user_id = ? AND log_date = ?
        """, (user_id, log_date))
        row = cursor.fetchone()
        return row["total"] if row else 0

def get_hydration_history(user_id: int, limit_days: int = 7, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT log_date, SUM(amount_ml) as total_ml
            FROM hydration_logs
            WHERE user_id = ?
            GROUP BY log_date
            ORDER BY log_date DESC
            LIMIT ?
        """, (user_id, limit_days))
        return [dict(r) for r in cursor.fetchall()]

# --- Daily Habit Logs Operations ---
def save_habit_log(user_id: int, log_date: str, data: Dict[str, Any], db_path: Optional[str] = None) -> bool:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO daily_habit_logs (
                user_id, log_date, sleep_hours, exercise_completed, diet_followed,
                fruits_veggies_consumed, daily_steps, mood_rating, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, log_date) DO UPDATE SET
                sleep_hours = excluded.sleep_hours,
                exercise_completed = excluded.exercise_completed,
                diet_followed = excluded.diet_followed,
                fruits_veggies_consumed = excluded.fruits_veggies_consumed,
                daily_steps = excluded.daily_steps,
                mood_rating = excluded.mood_rating,
                notes = excluded.notes;
        """, (
            user_id, log_date, data.get("sleep_hours", 0.0),
            data.get("exercise_completed", False), data.get("diet_followed", False),
            data.get("fruits_veggies_consumed", False), data.get("daily_steps", 0),
            data.get("mood_rating", 5), data.get("notes", "")
        ))
        return True

def get_habit_log_for_date(user_id: int, log_date: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_habit_logs WHERE user_id = ? AND log_date = ?", (user_id, log_date))
        row = cursor.fetchone()
        return dict(row) if row else None
