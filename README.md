# FitPlate India 🥗
### Personalized Indian Diet Planner & Health Analyzer

FitPlate India is a health and nutrition web application designed specifically for Indian food cultures, regional cuisines, and lifestyle realities. Built with **Python 3**, **Streamlit**, **SQLite**, and **Plotly**, it requires **zero paid external AI APIs**. By default it stores data locally. Hosted deployments store account and wellness data on the hosting provider, so review the provider's security and privacy terms before using real health information.

---

## 🌟 Key Features

1. **🔒 Account Security & Data Storage**
   - Cryptographically salted password hashing using **PBKDF2-HMAC-SHA256** (100,000 iterations).
   - Local runs keep data in a SQLite database on your computer.
   - Hosted runs use the configured persistent database disk; the hosting provider stores the data.
   - User account isolation: all queries filter strictly by authenticated session.

2. **🍛 Authentic Indian Diet Generator**
   - First-class support for **5 dietary patterns**:
     - *Vegetarian* (No meat, fish, or eggs)
     - *Eggetarian* (Vegetarian + eggs/egg whites)
     - *Non-Vegetarian* (Includes homestyle chicken and fish curries)
     - *Vegan* (Zero animal products, milk, paneer, curd, or ghee)
     - *Jain Vegetarian* (Strictly excludes onion, garlic, and root vegetables like potatoes, carrots, radishes)
   - Supports **5 regional Indian cuisines**: North Indian, South Indian, Maharashtrian, Gujarati, and Pan-Indian.
   - Comprehensive **Allergen & Sensitivity Filtering**: Dairy/Lactose, Gluten/Wheat, Peanuts/Nuts, Soy, Egg, Fish.
   - Rotational 7-day schedule with instant **"Swap Meal"** functionality.
   - Downloadable **CSV meal plan** and automatic **Weekly Indian Grocery Checklist with Budget Estimates (INR)**.

3. **🔬 Clinically Sound Energy & Health Calculations**
   - **Mifflin-St Jeor Equation** for accurate Basal Metabolic Rate (BMR) estimation.
   - **Asian-Indian Body Mass Index (BMI)** classification (noting elevated metabolic risk at BMI ≥ 23.0 kg/m²).
   - **Pediatric & Clinical Safety Guardrails**:
     - Blocks automated weight-loss calorie restriction for individuals under 18 years old.
     - Detects reported pregnancy, lactation, eating disorder history, and renal/cardiac conditions with explicit clinical referral advice instead of aggressive calorie deficits.

4. **💪 7-Day Joint-Friendly Exercise Scheduler**
   - Adaptable to Beginner, Intermediate, and Advanced fitness levels.
   - Scalable to available workout time (15, 20, 30, 45, 60 minutes) and home equipment.
   - Automatic injury modifications (e.g. knee-friendly glute bridges/leg raises instead of deep squats; back-safe neutral spine movements).

5. **💧 Water & Daily Habit Tracking**
   - Dynamic hydration target based on weight and activity level.
   - Quick-add buttons (`+150 ml`, `+250 ml`, `+500 ml`) and custom ml entry.
   - Daily habit checklist tracking sleep, diet adherence, workout completion, and mood.

6. **📈 Interactive Weight Progress Analytics**
   - Interactive Plotly chart displaying weight trajectory over time against your target goal line.
   - Milestone deltas, net change, and distance to target weight.

---

## 📂 Project Directory Structure

```text
fitplate_india/
│
├── app.py                      # Main application entry point & Streamlit page router
├── requirements.txt            # Python dependencies (Streamlit, Pandas, Plotly, etc.)
├── .env.example                # Template for configuration & environment variables
├── .gitignore                  # Git rules protecting database, secrets, and caches
├── config.py                   # Global constants, dietary categories, and formulas
├── database.py                 # SQLite relational database engine & parameterized CRUD
├── auth.py                     # PBKDF2-SHA256 password hashing & session management
├── models.py                   # Data models and structured schemas
├── utils.py                    # Unit conversions, formatting, and CSV plan export
│
├── data/
│   └── indian_foods.csv        # Comprehensive dataset of 58+ Indian dishes with macros & tags
│
├── services/
│   ├── __init__.py
│   ├── health_analyzer.py      # BMR (Mifflin-St Jeor), TDEE, macro & clinical safety logic
│   ├── diet_generator.py       # 7-day meal plan generator, meal swap & grocery engine
│   ├── exercise_generator.py   # 7-day workout scheduler with injury adaptations
│   ├── hydration.py            # Hydration target and progress calculator
│   └── progress.py             # Weight statistics and interactive Plotly charts
│
├── views/                      # Modular Streamlit UI screens
│   ├── __init__.py
│   ├── dashboard_view.py       # Central wellness dashboard with KPI cards & schedules
│   ├── profile_view.py         # Complete health profile form & input validation
│   ├── health_analysis_view.py # Detailed physiological report & nutritional breakdown
│   ├── diet_view.py            # 7-day meal schedule, swap buttons, CSV export, grocery list
│   ├── exercise_view.py        # 7-day workout routine with warmups and safety instructions
│   ├── hydration_view.py       # Interactive water logging & quick-add buttons
│   ├── progress_view.py        # Weight log entry, Plotly chart, and historical records
│   └── settings_view.py        # Privacy notice, account settings, and data deletion
│
└── tests/                      # Automated unit test suite (20 tests, 100% passing)
    ├── __init__.py
    ├── test_auth.py            # Password hashing, validation, and session tests
    ├── test_health_analyzer.py # BMI, BMR, pediatric & clinical safety tests
    ├── test_diet_generator.py  # Vegan, Jain, allergy, and 7-day meal plan tests
    ├── test_exercise_generator.py # Workout generation and joint injury adaptation tests
    └── test_database.py        # SQLite schema, CRUD operations, and cascade deletion tests
```

---

## 🚀 Step-by-Step Instructions to Run on Windows

### Step 1: Open the Project in VS Code
1. Open **Visual Studio Code**.
2. Click **File > Open Folder...** and select:
   `C:\Users\HP\.gemini\antigravity\scratch\fitplate_india`
3. Open a terminal inside VS Code by pressing `` Ctrl + ` `` (Backtick) or clicking **Terminal > New Terminal**.

### Step 2: (Optional) Set up a Virtual Environment
If you wish to use an isolated virtual environment:
```powershell
python -m venv .venv
```
Activate it:
- In PowerShell:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\.venv\Scripts\Activate.ps1
  ```
- Or in Command Prompt (`cmd`):
  ```cmd
  .venv\Scripts\activate.bat
  ```

### Step 3: Install Required Dependencies
Run:
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Automated Test Suite
To verify that all 20 tests pass:
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```
You will see `Ran 20 tests ... OK`.

### Step 5: Launch the Streamlit Web Application
Run:
```powershell
streamlit run app.py
```
Streamlit will automatically open your browser at:
👉 **`http://localhost:8501`**

## ☁️ Hosted Deployment (Render)

The included `render.yaml` configures a Streamlit web service with a persistent disk for SQLite. Persistent disks require a paid Render service. The database is stored by Render, so do not use this deployment for sensitive health information unless you have reviewed the provider's privacy, security, backup, and retention terms.

1. Push this project to a GitHub repository.
2. In Render, create a new Blueprint deployment and connect that repository.
3. Review the service and persistent-disk plan and its current cost before confirming deployment.
4. After deployment, use the HTTPS URL Render provides. Keep the Render service running for the URL to remain available.

The local `fitplate_india.db` is excluded from Git. Hosted accounts start with a new database on Render's persistent disk.

---

## 📖 How to Use FitPlate India

1. **Register & Log In**:
   - Go to the **Register** tab, enter your name, email, and a password (min. 6 characters).
   - Switch to the **Log In** tab and enter your credentials.
2. **Complete Your Health Profile**:
   - Navigate to **👤 My Health Profile**.
   - Enter your height, current weight, target weight, goal, and select your dietary preference (*Vegetarian, Jain, Vegan, Eggetarian, Non-Veg*).
   - Disclose any allergies or injuries (e.g. knee pain). Click **Save Health Profile**.
3. **Review Your Health Analysis**:
   - Navigate to **📊 Health Analysis** to inspect your Mifflin-St Jeor BMR, Total Daily Energy Expenditure (TDEE), target calorie budget, and macronutrient breakdown.
4. **Generate Your 7-Day Indian Diet Plan**:
   - Click **🥗 My Diet Plan** and click **Generate My 7-Day Plan Now**.
   - Browse Monday through Sunday tabs. Click **Swap This Dish** on any meal to replace it with another recipe, or toggle **Mark Eaten**.
   - Click **Download Plan (CSV)** to save your weekly schedule.
   - Open the **🛒 Weekly Indian Grocery List** expander to see estimated weekly shopping items and costs.
5. **Follow Your Workout Schedule**:
   - Click **🏋️ Weekly Exercise Plan** to see your 7-day routine tailored to your fitness level, available equipment, and joints.
6. **Track Hydration & Weight**:
   - Log glasses of water in **💧 Water Tracker** using quick-add buttons.
   - Record your weigh-ins in **📈 Progress Tracker** to see your interactive Plotly progress graph.

---

## 🩺 Clinical & Medical Wellness Notice
*FitPlate India is an educational wellness tool. It provides estimated nutritional guidance based on standard population formulas (Mifflin-St Jeor & ICMR South Asian reference intakes). It does not diagnose, treat, or cure any medical condition. Individuals with diagnosed clinical conditions (e.g., chronic kidney disease, heart failure, type 1 diabetes) or pregnant/lactating mothers should follow individualized care plans from a certified medical doctor or registered clinical dietitian.*
