# =========================
# 🤖 AI ENGINE (FINAL CLEAN VERSION)
# =========================

from openai import OpenAI
import os

# ✅ Uses environment variable (correct way)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================
# 💪 WORKOUT (UPDATED)
# =========================
def generate_workout(profile, progress):

    illness = str(profile.get("illness", "")).strip().lower()

    prompt = f"""
You are an elite AI fitness coach, rehabilitation specialist,
mobility expert, and recovery trainer.

Create a STRICTLY personalized 7-day workout plan.

USER PROFILE:
{profile}

PROGRESS DATA:
{progress}

HEALTH CONDITIONS:
{illness}

IMPORTANT RULES:

1. RUNNING GOAL:
- Include:
    • Easy Run
    • Interval Run
    • Long Run
- Include 2 strength days for runners
- Include mobility + recovery
- Avoid excessive bodybuilding workouts

2. FAT LOSS GOAL:
- Mix strength + cardio
- Higher calorie burn
- Moderate intensity
- Add recovery day

3. MUSCLE GAIN / STRENGTH:
- Focus resistance training
- Progressive overload
- Split muscle groups
- Less cardio

4. WEIGHT GAIN:
- Avoid excessive cardio
- Focus hypertrophy + recovery

5. GENERAL FITNESS:
- Balanced workouts
- Functional movement
- Mobility + conditioning

6. BEGINNER:
- Simple exercises
- Lower intensity
- More recovery

7. ADVANCED:
- Higher intensity
- Complex movements
- Athletic conditioning

8. PREGNANT:
- NO jumping
- NO HIIT
- NO risky core exercises
- Include walking, mobility, breathing

9. POSTPARTUM:
- Focus pelvic floor
- Core recovery
- Low-impact workouts
- Gradual progression

10. INJURIES:
- Avoid aggravating movements

11. HEALTH CONDITIONS:
If the user has any illness, injury, medical condition,
mobility issue, fatigue issue, thyroid issue,
heart issue, diabetes, PCOS, asthma,
joint pain, obesity, anxiety or stress:

- Avoid risky workouts
- Suggest safe exercises
- Prefer yoga, walking, stretching,
low-impact training, mobility,
recovery or beginner-friendly workouts when needed
- Consider fatigue and recovery limitations
- Avoid dangerous intensity recommendations
- Keep workouts realistic and sustainable

12. IF ILLNESS FIELD IS:
NA / N/A / NONE / NO / blank
→ Ignore illness completely

FORMAT:

Day 1:
- Warm-up
- Main Workout
- Duration
- Intensity
- Cool-down

IMPORTANT:
The workout MUST feel highly personalized.
Do NOT generate generic workouts.

The tone should feel premium, motivating,
modern and human-like.

This is NOT medical advice.
Only provide general wellness guidance.
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    return res.choices[0].message.content

# =========================
# 🥗 DIET (UPDATED)
# =========================
def generate_diet(profile, progress, cuisine, food_type, skin_type, skin_goal):

    illness = str(profile.get("illness", "")).strip().lower()

    prompt = f"""
You are an elite AI nutritionist,
sports dietician, wellness expert,
and recovery nutrition specialist.

Create a STRICT personalized 7-day diet plan.

USER PROFILE:
{profile}

PROGRESS:
{progress}

CUISINE:
{cuisine}

FOOD TYPE:
{food_type}

SKIN TYPE:
{skin_type}

SKIN GOAL:
{skin_goal}

HEALTH CONDITIONS:
{illness}

IMPORTANT RULES:

1. FAT LOSS:
- High protein
- Moderate calorie deficit
- Avoid excessive sugar
- Satiety-focused meals

2. MUSCLE GAIN:
- High protein
- Higher calories
- Recovery-focused meals
- Strength-support nutrition

3. RUNNING:
- Complex carbs
- Hydration
- Electrolytes
- Pre/post run meals

4. WEIGHT GAIN:
- Calorie surplus
- Nutrient-dense foods

5. PREGNANT:
- Iron
- Calcium
- Folate-rich foods
- Avoid unsafe foods

6. POSTPARTUM:
- Recovery foods
- Hydration
- Protein
- Iron-rich meals

7. ACNE / OILY SKIN:
- Lower processed sugar
- Anti-inflammatory foods

8. DRY SKIN:
- Healthy fats
- Hydration-rich foods

9. GLOW GOAL:
- Antioxidants
- Fruits
- Hydration

10. HEALTH CONDITIONS:
If user has:
- Diabetes
- Thyroid
- PCOS
- Heart issues
- Cholesterol
- High BP
- Fatigue
- Obesity
- Acidity
- Digestion issues
- Stress/anxiety

Then:
- Suggest safer nutrition
- Avoid harmful foods
- Include balanced meals
- Include recovery support
- Include hydration guidance
- Avoid extreme dieting

11. IF ILLNESS FIELD IS:
NA / N/A / NONE / NO / blank
→ Ignore illness completely

INCLUDE:
- Morning drink
- Breakfast
- Mid snack
- Lunch
- Evening snack
- Dinner
- Timing
- Portions
- Hydration

ALSO INCLUDE:
- Foods to avoid
- Skin-friendly foods
- Recovery recommendations
- Lifestyle suggestions

IMPORTANT:
The plan MUST feel deeply personalized.

Do NOT generate generic meal plans.

Tone should feel premium,
modern, motivating and human-like.

This is NOT medical advice.
Only provide general wellness guidance.
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    return res.choices[0].message.content

# =========================
# 🧠 COACH
# =========================
def coach_reply(question, profile):

    prompt = f"""
User Profile:
{profile}

Question:
{question}

Give smart, practical fitness advice.
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# =========================
# 🧘 STRESS RELIEF
# =========================
def stress_relief(profile):

    prompt = f"""
User Profile:
{profile}

Give stress relief suggestions including:
- Meditation
- Fun activities
- Music
- Relaxation ideas
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# =========================
# 💃 ZUMBA (UPDATED ✅)
# =========================
def generate_zumba():

    prompt = """
Give 3 Zumba YouTube video links with titles.

Format:
1. Title - https://youtube.com/...
2. Title - https://youtube.com/...
3. Title - https://youtube.com/...
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# ---------- EYE CARE ----------
def generate_eye_care(profile):

    prompt = f"""
Give personalized eye care tips.

User Profile:
{profile}

Include:
- Screen-time protection
- Eye relaxation
- Sleep advice
- Hydration
- Eye exercises
- Workplace eye care

DO NOT include:
- Workout advice
- Fat loss advice
- Gym recommendations
- Nutrition plans

Keep it practical and concise.
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    return res.choices[0].message.content
