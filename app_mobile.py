import re
import os
import json
import time
from io import BytesIO
from datetime import date
import cv2
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import base64
from ai_engine import (
    generate_workout,
    generate_diet,
    coach_reply,
    stress_relief,
    generate_zumba,
    generate_eye_care,
)
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# =========================
# ANALYTICS STATE
# =========================
if "show_analytics" not in st.session_state:
    st.session_state.show_analytics = False

# =========================
# PAGE CONFIG (MUST BE FIRST)
# =========================
st.set_page_config(
    page_title="AIVioMate",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LOGO_URL = "https://imgcdn.stablediffusionweb.com/2025/8/29/c87b3fbd-f0fc-46c6-9334-a431484cc041.jpg"

st.markdown(
    """
<style>
.streamlit-expanderHeader {
    background-color: #081028 !important;
    color: white !important;
    border-radius: 10px !important;
}
.streamlit-expanderContent {
    background-color: #081028 !important;
    color: white !important;
    border-radius: 10px !important;
}
details {
    background-color: #081028 !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.08);
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# GLOBAL CSS
# =========================
st.markdown(
    """
<style>
div.stDownloadButton > button {
    background-color: #6C63FF !important;
    color: white !important;
    border-radius: 8px;
    font-weight: 600;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
div[role="radiogroup"] label {
    background: rgba(99,102,241,0.12);
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
    color: white !important;
}
div[role="radiogroup"] label:hover {
    background: rgba(139,92,246,0.3);
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #111827);
    color: white;
}
.main .block-container {
    max-width: 1150px;
    padding-top: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}
div[data-testid="stFileUploader"] {
    background-color: transparent !important;
}
.card {
    background: rgba(255,255,255,0.06);
    padding: 16px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(8px);
}
h1, h2, h3, h4, label {
    color: white !important;
}
.stButton button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white !important;
    border-radius: 10px;
    height: 42px;
    width: 100% !important;
    border: none;
    font-weight: 600;
    transition: all 0.25s ease;
}
.stButton button:hover {
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
}
.stSlider label {
    color: #ddd;
}
input, textarea {
    background-color: #0e2a47 !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
}
input::placeholder {
    color: #aaa !important;
}
div[data-baseweb="input"] > div {
    background-color: #0e2a47 !important;
    border-radius: 10px;
}
div[data-baseweb="input"] input:focus {
    outline: none !important;
    border: 1px solid #6366f1 !important;
}
div[data-baseweb="select"] > div {
    background-color: #0e2a47 !important;
    color: white !important;
    border-radius: 8px;
}
img {
    border-radius: 14px;
    object-fit: cover;
}
.stProgress > div > div {
    background: linear-gradient(90deg, #22c55e, #4ade80);
}
.user-bubble {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    padding: 10px 14px;
    border-radius: 12px;
    color: white;
    margin: 8px 0;
    max-width: 85%;
    width: fit-content;
    margin-left: auto;
}
.bot-bubble {
    background: rgba(255,255,255,0.08);
    padding: 10px 14px;
    border-radius: 12px;
    color: white;
    margin: 8px 0;
    max-width: 85%;
    width: fit-content;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #081028, #0b1736);
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: white !important;
}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: rgba(255,255,255,0.05);
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 8px;
}
.stat-card {
    display: none;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
div[data-testid="stAlert"] {
    color: white !important;
}
details {
    color: white !important;
}
details p {
    color: white !important;
}
.stAlert p {
    color: white !important;
}
p {
    color: white !important;
}
@media (max-width: 768px) {
    h1 { font-size: 28px !important; }
    h2 { font-size: 24px !important; }
    h3 { font-size: 20px !important; }
    .stButton button { height: 40px; font-size: 14px; }
    .main .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
img {
    border-radius: 18px;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# SESSION STATE DEFAULTS
# =========================
st.session_state.setdefault("streak", 0)
st.session_state.setdefault("last_visit", None)
st.session_state.setdefault("best_streak", 0)

if "page" not in st.session_state:
    st.session_state.page = "Profile"
if "profile_history" not in st.session_state:
    st.session_state.profile_history = []
if "plan_history" not in st.session_state:
    st.session_state.plan_history = []
if "ai_memory" not in st.session_state:
    st.session_state.ai_memory = {
        "workout_history": [],
        "diet_history": [],
        "coach_history": [],
    }

# =========================
# HELPER FUNCTIONS
# =========================


def clean_html(text):
    return re.sub(r"<.*?>", "", str(text or "")).strip()


def make_pdf_bytes(text, title="Report"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = [Paragraph(f"<b>{title}</b>", styles["Heading2"])]
    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))
    doc.build(content)
    buffer.seek(0)
    return buffer


def update_memory(type_key, result):
    if "plan_history" not in st.session_state:
        st.session_state["plan_history"] = []
    history = st.session_state["plan_history"]
    if history and history[-1].get("content") == result:
        return
    history.append(
        {
            "type": type_key.replace("_history", "").capitalize(),
            "date": str(pd.Timestamp.today().date()),
            "content": result,
            "favorite": False,
        }
    )
    st.session_state["plan_history"] = history


def get_memory(type):
    return st.session_state.ai_memory.get(type, [])


def analyze_progress():
    history = st.session_state.get("profile_history", [])
    if len(history) < 2:
        return "no_data"
    df = pd.DataFrame(history)
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")
    df = df.dropna().sort_values("date")
    change = df["weight"].iloc[-1] - df["weight"].iloc[0]
    if change < -1:
        return "losing"
    elif -1 <= change <= 1:
        return "stuck"
    else:
        return "gaining"


def get_user_profile():
    return f"""
Age: {st.session_state.get('age_input')}
Gender: {st.session_state.get('gender_input')}
Condition: {st.session_state.get('condition_input')}
Height: {st.session_state.get('height_input')}
Weight: {st.session_state.get('weight_input')}
Goal: {st.session_state.get('goal_input')}
Level: {st.session_state.get('level_input')}
Lifestyle: {st.session_state.get('lifestyle_input')}
Sleep: {st.session_state.get('sleep_input')}
Injury: {st.session_state.get('injury_input')}
"""


def get_progress():
    return str(st.session_state.get("profile_history", []))


def detect_intent(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["workout", "exercise", "gym", "form", "sets", "reps"]):
        return "workout"
    if any(k in t for k in ["diet", "food", "meal", "recipe", "nutrition"]):
        return "nutrition"
    if any(k in t for k in ["stress", "sleep", "relax", "anxiety"]):
        return "wellness"
    return "general"


def extract_links(text):
    return re.findall(r"https?://[^\s]+", text)


MEMORY_FILE = "coach_memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f)


# =========================
# SESSION STATE DEFAULTS
# =========================
if "profile_data" not in st.session_state:
    st.session_state["profile_data"] = {}

if "progress_data" not in st.session_state:
    st.session_state["progress_data"] = {}

if "water" not in st.session_state:
    st.session_state["water"] = 0

if "sleep" not in st.session_state:
    st.session_state["sleep"] = 0

if "stress" not in st.session_state:
    st.session_state["stress"] = 0

if "energy" not in st.session_state:
    st.session_state["energy"] = 0

if "mood" not in st.session_state:
    st.session_state["mood"] = None

if "analytics_data" not in st.session_state:
    st.session_state["analytics_data"] = []

# =========================
# SIDEBAR NAVIGATION
# =========================
with st.sidebar:

    st.image(LOGO_URL, width=80)

    st.markdown(
        """
        <h2 style="margin-bottom:0px;">⚡ AIVioMate</h2>
        <p style="margin-top:0px; opacity:0.7; font-size:14px;">AI Wellness Companion</p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    tabs = ["Profile", "Dashboard", "Workout", "Nutrition", "Coach", "Wellness"]

    selected_page = st.radio(
        " ",
        tabs,
        index=tabs.index(st.session_state.page),
    )

    st.session_state.page = selected_page

    st.markdown("---")

    st.caption("Train smarter • Recover better")

page = st.session_state.page


# =========================
# PROFILE PAGE
# =========================
if page == "Profile":

    # =========================
    # HERO CARD
    # =========================
    st.markdown(
        """
        <div style="
        background: rgba(255,255,255,0.05);
        padding:20px;
        border-radius:16px;
        margin-bottom:22px;
        border:1px solid rgba(255,255,255,0.08);
        ">
        <h2 style="margin-bottom:6px;">🚀 Welcome to AIVioMate</h2>
        <p style="opacity:0.8; font-size:15px; margin-bottom:0px;">
        Your AI-powered wellness companion for fitness,
        nutrition, recovery & performance tracking.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =========================
    # HOW TO USE APP
    # =========================
    with st.expander("✨ How To Use The App", expanded=False):

        st.markdown(
            """
            <div style='font-size:15px;'>
            <h3>👤 Step 1 — Complete Your Profile</h3>
            Fill:
            <ul>
                <li>Age</li>
                <li>Weight</li>
                <li>Fitness Goal</li>
                <li>Lifestyle</li>
                <li>Activity Level</li>
            </ul>
            AI uses this data to personalize all recommendations.
            <hr>
            <h3>📊 Dashboard</h3>
            Track:
            <ul>
                <li>Sleep</li>
                <li>Stress</li>
                <li>Hydration</li>
                <li>Energy</li>
                <li>Wellness Score</li>
            </ul>
            <hr>
            <h3>💪 Workout</h3>
            Generate:
            <ul>
                <li>Fat loss plans</li>
                <li>Running programs</li>
                <li>Strength routines</li>
                <li>Recovery workouts</li>
            </ul>
            <hr>
            <h3>🥗 Nutrition</h3>
            Get:
            <ul>
                <li>Personalized diets</li>
                <li>Skin-focused nutrition</li>
                <li>Cuisine-based meal plans</li>
            </ul>
            <hr>
            <h3>🤖 AI Coach</h3>
            Ask questions anytime about:
            <ul>
                <li>Fitness</li>
                <li>Recovery</li>
                <li>Nutrition</li>
                <li>Stress</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # PROFILE FORM
    # =========================
    st.markdown(
        """
        <h2 style='margin-bottom:4px;'>👤 Your Profile</h2>
        <p style='opacity:0.75;'>Tell us about yourself to personalize your plans</p>
        """,
        unsafe_allow_html=True,
    )

    # =========================
    # BASIC DETAILS
    # =========================
    st.markdown("### Basic Information")

    age = st.text_input("Age", placeholder="Enter your age", key="age_input")

    gender = st.selectbox(
        "Gender",
        ["Select", "Male", "Female", "Other"],
        key="gender_input",
    )

    if gender == "Female":

        try:
            age_val = int(age)
        except Exception:
            age_val = 0

        if age_val < 18:
            special_condition = "N/A"
            st.session_state["condition_input"] = "N/A"
            st.info("⚠️ Special conditions not applicable for this age")
        else:
            special_condition = st.selectbox(
                "Special Condition",
                ["None", "Pregnant", "Postpartum"],
                key="condition_input",
            )

    else:
        special_condition = "N/A"
        st.session_state["condition_input"] = "N/A"

    height = st.text_input(
        "Height (cm)", placeholder="Enter your height", key="height_input"
    )
    weight = st.text_input(
        "Weight (kg)", placeholder="Enter your weight", key="weight_input"
    )
    target_weight = st.text_input("Target Weight (kg)", key="target_weight_input")

    # =========================
    # BMI
    # =========================
    if height and weight:

        try:
            h = float(height) / 100
            w = float(weight)
            bmi = round(w / (h**2), 2)

            if bmi < 18.5:
                status = "Underweight ❗"
                color = "#ef4444"
            elif bmi < 25:
                status = "Normal ✅"
                color = "#22c55e"
            else:
                status = "Overweight ⚠️"
                color = "#f59e0b"

            ideal_min = round(18.5 * (h**2), 1)
            ideal_max = round(24.9 * (h**2), 1)

            st.markdown(
                f"""
                <div style="
                background:rgba(255,255,255,0.05);
                padding:14px;
                border-radius:12px;
                margin-top:10px;
                margin-bottom:18px;
                border-left:4px solid {color};
                ">
                <h4 style='margin-top:0px;'>📊 BMI Analysis</h4>
                <p><b>BMI:</b> <span style='color:{color};'>{bmi} ({status})</span></p>
                <p style='margin-bottom:0px;'>🎯 Ideal Weight Range: {ideal_min} - {ideal_max} kg</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        except Exception:
            st.warning("Enter valid height and weight")

    # =========================
    # FITNESS DETAILS
    # =========================
    st.markdown("### Fitness Preferences")

    goal = st.selectbox(
        "Goal",
        [
            "Select Goal",
            "Fat Loss",
            "Strength Training",
            "Muscle Gain",
            "Weight Gain",
            "General Fitness",
            "Running",
        ],
        key="goal_input",
    )

    level = st.selectbox(
        "Fitness Level",
        ["Select Level", "Beginner", "Intermediate", "Advanced"],
        key="level_input",
    )

    lifestyle = st.selectbox(
        "Lifestyle",
        [
            "Select Lifestyle",
            "Sedentary (desk job)",
            "Moderately Active",
            "Very Active",
        ],
        key="lifestyle_input",
    )

    sleep_pref = st.slider("Average Sleep (hrs)", 0, 10, 6, key="sleep_input")

    injury = st.selectbox(
        "Injury",
        ["None", "Knee Pain", "Back Pain", "Ankle Pain", "Shoulder Pain"],
        key="injury_input",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # SAVE PROFILE
    # =========================
    if st.button("💾 Save Profile"):

        if (
            not age
            or not height
            or not weight
            or goal == "Select Goal"
            or level == "Select Level"
            or lifestyle == "Select Lifestyle"
        ):
            st.warning("⚠️ Please fill all required fields")

        else:
            import datetime

            st.success("✅ Profile saved successfully!")

            st.session_state["profile_data"] = {
                "age": age,
                "gender": gender,
                "condition": special_condition,
                "height": height,
                "weight": weight,
                "target_weight": target_weight,
                "goal": goal,
                "level": level,
                "lifestyle": lifestyle,
                "sleep": sleep_pref,
                "injury": injury,
            }

            if "profile_history" not in st.session_state:
                st.session_state["profile_history"] = []

            st.session_state["profile_history"].append(
                {
                    "date": datetime.datetime.now(),
                    "weight": weight,
                }
            )

    # =========================
    # RESET PROFILE
    # =========================
    if st.button("Reset Profile"):

        st.session_state["profile_data"] = {}
        st.session_state["progress_data"] = {}

        st.success("✅ Profile reset successfully")

        st.rerun()


# =========================
# DASHBOARD PAGE
# =========================
elif page == "Dashboard":

    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import random
    import datetime

    # =========================
    # STATE
    # =========================
    if "analytics_mode" not in st.session_state:
        st.session_state.analytics_mode = False

    if "water" not in st.session_state:
        st.session_state.water = 0

    if "mood" not in st.session_state:
        st.session_state.mood = "Okay"

    # =====================================================
    # DASHBOARD VIEW
    # =====================================================
    if not st.session_state.show_analytics:

        # =========================
        # WELLNESS TIP CARD
        # =========================
        st.markdown(
            """
<div style="
background:rgba(99,102,241,0.10);
padding:20px;
border-radius:18px;
border:1px solid rgba(255,255,255,0.06);
margin-bottom:25px;
">

<h3 style="color:white;">
🔥 Wellness Tip
</h3>

<p style="
color:#d1d5db;
font-size:15px;
line-height:1.7;
margin-bottom:0;
">
Consistency beats intensity.
Focus on sleep, hydration,
movement and recovery daily.
</p>

</div>
""",
            unsafe_allow_html=True,
        )

        # =========================
        # HERO IMAGE
        # =========================
        img_left, img_center, img_right = st.columns([1, 2.2, 1])

        with img_center:
            st.image(
                "https://images.unsplash.com/photo-1517836357463-d25dfeac3438",
                use_container_width=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # =========================
        # DAILY CHECK-IN
        # =========================
        st.markdown("## 🧠 Daily Check-in")
        st.caption("Track recovery, hydration, stress and wellness daily.")
        st.markdown("<br>", unsafe_allow_html=True)

        # =========================
        # SLIDERS
        # =========================
        c1, c2 = st.columns(2)

        with c1:
            sleep = st.slider("Sleep (hrs)", 0, 12, st.session_state.get("sleep", 6))
            st.session_state.sleep = sleep

        with c2:
            stress = st.slider("Stress", 0, 10, st.session_state.get("stress", 4))
            st.session_state.stress = stress

        energy = st.slider("Energy", 0, 10, st.session_state.get("energy", 6))
        st.session_state.energy = energy

        st.markdown("<br>", unsafe_allow_html=True)

        # =========================
        # EMOTIONAL HEALTH
        # =========================
        st.markdown("## 😊 Emotional Health")

        moods = [
            ("😔", "Low", 2),
            ("😐", "Okay", 5),
            ("🙂", "Good", 8),
            ("😄", "Great", 10),
        ]

        mood_cols = st.columns(4)

        for i, (emoji, label, score_value) in enumerate(moods):

            with mood_cols[i]:

                st.markdown(
                    f"""
    <div style="
    font-size:14px;
    font-weight:600;
    margin-bottom:8px;
    color:white;
    text-align:left;
    ">
    {label}
    </div>
    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    emoji,
                    key=f"mood_{i}",
                ):
                    st.session_state.mood = label
                    st.session_state.mood_value = score_value
                    st.rerun()

        current_mood = st.session_state.get("mood", "Not Selected")

        st.caption(f"Current Mood: {current_mood}")

        # =========================
        # WELLNESS SCORE
        # =========================
        st.markdown("---")
        st.markdown("### 🚀 Wellness Score")

        mood_map = {
            "Low": 3,
            "Okay": 5,
            "Good": 8,
            "Great": 10,
        }

        mood_value = mood_map.get(st.session_state.get("mood"), 0)

        # =========================
        # INDIVIDUAL SCORES
        # =========================
        sleep_score = sleep * 10
        stress_score = (10 - stress) * 10 if stress > 0 else 0
        energy_score = energy * 10
        water_score = st.session_state.water * 10
        mood_score = mood_value * 10

        # =========================
        # CHECK IF USER ENTERED ANYTHING
        # =========================
        has_inputs = any(
            [
                sleep > 0,
                stress > 0,
                energy > 0,
                st.session_state.water > 0,
                mood_value > 0,
            ]
        )

        # =========================
        # FINAL SCORE
        # =========================
        if not has_inputs:
            score = 0
            color = "#6b7280"
            label = "Start Check-In"

        else:
            values = []

            if sleep > 0:
                values.append(sleep * 10)
            if stress > 0:
                values.append((10 - stress) * 10)
            if energy > 0:
                values.append(energy * 10)
            if st.session_state.water > 0:
                values.append(st.session_state.water * 10)
            if mood_value > 0:
                values.append(mood_value * 10)

            score = min(int(sum(values) / len(values)), 100)

            color = "#ef4444" if score < 40 else "#f59e0b" if score < 70 else "#22c55e"
            label = (
                "Needs Attention"
                if score < 40
                else "Good" if score < 70 else "Excellent"
            )

        fig = go.Figure(
            data=[
                go.Pie(
                    values=[score, 100 - score],
                    hole=0.72,
                    rotation=90,
                    textinfo="none",
                    marker=dict(colors=[color, "#1f2937"]),
                )
            ]
        )

        fig.update_layout(
            width=240,
            height=240,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=False,
            annotations=[
                dict(
                    text=f"<b>{score}</b><br>{label}",
                    x=0.5,
                    y=0.5,
                    font=dict(size=26, color="white"),
                    showarrow=False,
                )
            ],
        )

        col1, col2, col3 = st.columns([1, 1.2, 1])

        with col2:
            st.plotly_chart(
                fig,
                config={"displayModeBar": False},
                use_container_width=False,
            )

        # =========================
        # SMART TIPS
        # =========================
        st.markdown("### 💡 Smart Tips")

        tips = []
        if sleep < 6:
            tips.append("😴 Improve your sleep schedule")
        if stress > 7:
            tips.append("🧘 High stress detected today")
        if st.session_state.water < 5:
            tips.append("💧 Increase hydration")
        if energy < 5:
            tips.append("⚡ Prioritize recovery")
        if not tips:
            tips.append("🔥 Excellent consistency today")

        for tip in tips:
            st.markdown(
                f"""
<div style="
background:rgba(99,102,241,0.10);
padding:14px;
border-radius:12px;
margin-bottom:10px;
border:1px solid rgba(255,255,255,0.06);
color:white;
">
{tip}
</div>
""",
                unsafe_allow_html=True,
            )

        if st.button(
            "📈 Open Detailed Analytics",
            use_container_width=True,
        ):
            st.session_state.show_analytics = True
            st.rerun()

        # =========================
        # RESET DAILY CHECK-IN
        # =========================
        if st.button(
            "🔄 Reset Daily Check-In",
            use_container_width=True,
        ):
            st.session_state["water"] = 0
            st.session_state["sleep"] = 0
            st.session_state["stress"] = 0
            st.session_state["energy"] = 0
            st.session_state["mood"] = None

            st.rerun()

    # =====================================================
    # ANALYTICS PAGE
    # =====================================================
    else:

        # =========================
        # CUSTOM STYLING
        # =========================
        st.markdown(
            """
<style>

/* MAIN APP */
.stApp {
    background-color: #07122b;
    color: white;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #081028 0%, #07122b 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* SIDEBAR TEXT */
[data-testid="stSidebar"] * {
    color: white !important;
}

/* BUTTONS */
.stButton > button {
    background: linear-gradient(90deg,#6366f1,#8b5cf6);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.7rem 1rem;
    font-weight: 600;
}

.stButton > button:hover {
    opacity: 0.92;
    color: white;
}

/* HEADINGS */
h1, h2, h3 {
    color: #ffffff !important;
    opacity: 1 !important;
}

/* TEXT */
p, label, span, div {
    color: #ffffff !important;
    opacity: 1 !important;
}

/* REMOVE STREAMLIT GREY */
.block-container {
    padding-top: 2rem;
}

</style>
""",
            unsafe_allow_html=True,
        )

        # =========================
        # BACK BUTTON
        # =========================
        if st.button(
            "⬅ Back to Dashboard",
            use_container_width=True,
        ):
            st.session_state.show_analytics = False
            st.rerun()

        # =========================
        # HEADER
        # =========================
        st.markdown("## 📊 Performance Insights")

        st.caption("Monitor your wellness trends over time.")

        # =========================
        # DUMMY DATA
        # =========================
        if (
            "analytics_data" not in st.session_state
            or len(st.session_state.analytics_data) == 0
        ):
            st.session_state.analytics_data = []

            base_date = datetime.datetime.now()

            for i in range(14):
                st.session_state.analytics_data.append(
                    {
                        "date": base_date - datetime.timedelta(days=13 - i),
                        "sleep": random.randint(5, 9),
                        "stress": random.randint(2, 8),
                        "energy": random.randint(4, 10),
                        "water": random.randint(3, 8),
                        "wellness_score": random.randint(55, 95),
                    }
                )

        # =========================
        # DATAFRAME
        # =========================
        df = pd.DataFrame(st.session_state.analytics_data)

        df["date"] = pd.to_datetime(df["date"])

        # =========================
        # CHARTS
        # =========================
        metrics = [
            ("sleep", "😴 Sleep Trend"),
            ("stress", "🧘 Stress Trend"),
            ("energy", "⚡ Energy Trend"),
            ("water", "💧 Hydration Trend"),
            ("wellness_score", "🚀 Wellness Score"),
        ]

        for metric, title in metrics:

            st.markdown(f"## {title}")

            fig = px.line(
                df,
                x="date",
                y=metric,
                markers=True,
            )

            # =========================
            # LINE STYLE
            # =========================
            fig.update_traces(
                line=dict(
                    color="#38bdf8",
                    width=3,
                ),
                marker=dict(
                    size=7,
                    color="#38bdf8",
                ),
            )

            # =========================
            # CHART LAYOUT
            # =========================
            fig.update_layout(
                paper_bgcolor="#07122b",
                plot_bgcolor="#0b1736",
                font=dict(color="white"),
                height=320,
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20,
                ),
                xaxis=dict(
                    showgrid=False,
                    color="#cbd5e1",
                ),
                yaxis=dict(
                    gridcolor="rgba(255,255,255,0.12)",
                    zeroline=False,
                    color="#cbd5e1",
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            )

            st.markdown("<br>", unsafe_allow_html=True)


# =========================
# WORKOUT PAGE
# =========================
elif page == "Workout":

    st.subheader("💪 Workout Plans")
    st.info("👉 Complete your Profile for highly personalized workout recommendations")

    st.image(
        "https://images.unsplash.com/photo-1599058917212-d750089bc07e",
        width=700,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # GENERATE WORKOUT
    # =========================
    if st.button("🚀 Generate AI Workout", use_container_width=True):

        profile_data = st.session_state.get("profile_data", {})
        progress = st.session_state.get("progress_data", {})
        required_fields = ["age", "weight", "goal", "level"]

        missing = [
            field
            for field in required_fields
            if not profile_data.get(field)
            or str(profile_data.get(field)).startswith("Select")
        ]

        if missing:
            st.warning("⚠️ Complete your Profile page before generating workout plans.")
        else:
            result = generate_workout(profile_data, progress)
            st.session_state["workout_result"] = result
            update_memory("workout_history", result)
            st.success("✅ Workout plan generated successfully")

    # =========================
    # SHOW RESULT
    # =========================
    if "workout_result" in st.session_state:

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<h2 style='margin-bottom:8px;'>🏋️ Your Workout Plan</h2>",
            unsafe_allow_html=True,
        )

        clean_text = re.sub(r"<.*?>", "", st.session_state["workout_result"])

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        content = []

        for line in clean_text.split("\n"):
            content.append(Paragraph(line, styles["Normal"]))

        doc.build(content)
        buffer.seek(0)

        st.download_button(
            "📄 Download Workout Plan",
            buffer,
            file_name="workout_plan.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="
            background:rgba(255,255,255,0.04);
            padding:18px;
            border-radius:16px;
            border:1px solid rgba(255,255,255,0.08);
            ">
            {clean_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =========================
    # ZUMBA SECTION
    # =========================
    st.markdown(
        """
        <div style="
        background:rgba(99,102,241,0.12);
        padding:18px;
        border-radius:16px;
        border:1px solid rgba(139,92,246,0.3);
        margin-bottom:18px;
        ">
        <h3 style='margin-top:0px;'>💃 Dance & Zumba Workouts</h3>
        <p style='opacity:0.8; margin-bottom:0px;'>
        Looking for something fun, energetic & beginner-friendly?
        Try dance-based fitness routines.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("💃 Show Zumba Workout", use_container_width=True):

        result = generate_zumba()

        st.markdown(
            "<h3 style='margin-bottom:10px;'>💃 Zumba Workout Plan</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="
            background:rgba(255,255,255,0.04);
            padding:18px;
            border-radius:16px;
            border:1px solid rgba(255,255,255,0.08);
            ">
            {result}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =========================
    # WORKOUT HISTORY
    # =========================
    st.markdown(
        "<h2 style='margin-bottom:12px;'>📚 Workout History</h2>",
        unsafe_allow_html=True,
    )

    history = st.session_state.get("plan_history", [])
    workouts = [h for h in history if h["type"].lower() == "workout"]

    if workouts:
        for item in reversed(workouts[-5:]):
            with st.expander(f"💪 {item['date']}", expanded=False):
                st.markdown(item["content"])
    else:
        st.info("No workout history yet.")


# =========================
# NUTRITION PAGE
# =========================
elif page == "Nutrition":

    st.subheader("🥗 Nutrition Plans")

    st.image(
        "https://libapps-au.s3-ap-southeast-2.amazonaws.com/accounts/97668/images/teadergrafik_nutritions.jpg",
        width=700,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # NUTRITION FORM CARD
    # =========================
    st.markdown(
        """
        <div style="
        background:rgba(255,255,255,0.04);
        padding:18px;
        border-radius:16px;
        margin-bottom:22px;
        border:1px solid rgba(255,255,255,0.08);
        ">
        """,
        unsafe_allow_html=True,
    )

    cuisine = st.selectbox(
        "Cuisine",
        ["Select Cuisine", "Indian", "South Indian", "North Indian", "Continental"],
    )

    food_type = st.selectbox(
        "Food Type",
        ["Select Food Type", "Veg", "Non-Veg", "Vegan"],
    )

    st.markdown(
        "<h3 style='margin-top:18px; margin-bottom:8px;'>✨ Skin Preferences</h3>",
        unsafe_allow_html=True,
    )

    skin_type = st.selectbox(
        "Skin Type",
        ["Select Skin Type", "Dry", "Sensitive", "Oily", "Combination", "Acne-prone"],
    )

    skin_goal = st.selectbox(
        "Skin Goal",
        ["Select Skin Goal", "Acne Control", "Glow", "Anti-aging", "Pigmentation"],
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # GENERATE DIET
    # =========================
    if st.button("🚀 Generate Nutrition Plan", use_container_width=True):

        profile_data = st.session_state.get("profile_data", {})
        progress = st.session_state.get("progress_data", {})
        required_fields = ["age", "weight", "goal", "level"]

        missing = [
            field
            for field in required_fields
            if not profile_data.get(field)
            or str(profile_data.get(field)).startswith("Select")
        ]

        if missing:
            st.warning(
                "⚠️ Please complete your Profile page before generating a personalized nutrition plan."
            )
        else:
            final_profile = {
                **profile_data,
                "cuisine": cuisine,
                "food_type": food_type,
                "skin_type": skin_type,
                "skin_goal": skin_goal,
            }

            result = generate_diet(
                final_profile, progress, cuisine, food_type, skin_type, skin_goal
            )
            st.session_state["diet_result"] = result
            update_memory("diet_history", result)
            st.success("✅ Nutrition plan generated successfully")

    # =========================
    # SHOW RESULT
    # =========================
    if "diet_result" in st.session_state:

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<h2 style='margin-bottom:8px;'>🍽️ Your Nutrition Plan</h2>",
            unsafe_allow_html=True,
        )
        st.success("🥗 Personalized for your lifestyle & skin goals")
        st.caption("💊 Supplement suggestions are general wellness recommendations")

        clean_text = re.sub(r"<.*?>", "", st.session_state["diet_result"])

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        content = []

        for line in clean_text.split("\n"):
            content.append(Paragraph(line, styles["Normal"]))

        doc.build(content)
        buffer.seek(0)

        st.download_button(
            "📄 Download Diet Plan",
            buffer,
            file_name="diet_plan.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="
            background:rgba(255,255,255,0.04);
            padding:18px;
            border-radius:16px;
            border:1px solid rgba(255,255,255,0.08);
            ">
            {clean_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =========================
    # NUTRITION HISTORY
    # =========================
    st.markdown(
        "<h2 style='margin-bottom:12px;'>📚 Nutrition History</h2>",
        unsafe_allow_html=True,
    )

    history = st.session_state.get("plan_history", [])
    diets = [h for h in history if h["type"].lower() == "diet"]

    if diets:
        for item in reversed(diets[-5:]):
            with st.expander(f"🥗 {item['date']}", expanded=False):
                st.markdown(item["content"])
    else:
        st.info("No nutrition history yet.")


# =========================
# COACH PAGE
# =========================
elif page == "Coach":

    # =========================
    # INIT STATES
    # =========================
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "prefill" not in st.session_state:
        st.session_state.prefill = ""

    st.subheader("🤖 AI Wellness Coach")

    st.image(
        "https://coachvox.ai/wp-content/uploads/2023/04/AI-enhanced-coaching.jpg",
        width=700,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # QUICK SUGGESTIONS
    # =========================
    st.markdown(
        "<h3 style='margin-bottom:10px;'>💡 Quick Suggestions</h3>",
        unsafe_allow_html=True,
    )

    suggestions = [
        "Give me a workout for fat loss",
        "Easy high-protein breakfast ideas",
        "How to reduce stress quickly",
    ]

    for q in suggestions:
        if st.button(q, use_container_width=True):
            st.session_state.prefill = q

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # CHAT HISTORY
    # =========================
    if st.session_state.chat_history:
        st.markdown(
            "<h3 style='margin-bottom:14px;'>💬 Conversation</h3>",
            unsafe_allow_html=True,
        )

    for msg in st.session_state.chat_history:

        cls = "user-bubble" if msg["role"] == "user" else "bot-bubble"

        st.markdown(
            f'<div class="{cls}">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )

    # =========================
    # INPUT BOX
    # =========================
    user_input = st.text_input(
        "Ask your coach...",
        value=st.session_state.prefill,
        key="coach_input",
        placeholder="Ask about workouts, nutrition, recovery, stress...",
    )

    # =========================
    # GET GUIDANCE
    # =========================
    if st.button("🚀 Get Guidance", use_container_width=True) and user_input:

        st.session_state.chat_history.append({"role": "user", "content": user_input})

        profile = get_user_profile()
        reply = coach_reply(user_input, profile)

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.session_state.prefill = ""
        st.rerun()

    # =========================
    # RECENT CONVERSATIONS
    # =========================
    st.markdown(
        "<h2 style='margin-bottom:12px;'>📚 Recent Conversations</h2>",
        unsafe_allow_html=True,
    )

    if st.session_state.chat_history:

        recent = st.session_state.chat_history[-6:]

        for msg in recent:
            role = "🧑 You" if msg["role"] == "user" else "🤖 Coach"
            with st.expander(role, expanded=False):
                st.markdown(msg["content"])

    else:
        st.info("No conversations yet.")


# =========================
# WELLNESS PAGE
# =========================
elif page == "Wellness":

    st.subheader("🌿 Wellness & Recovery")

    tab1, tab2, tab3 = st.tabs(
        ["🧘 Stress Relief", "👁️ Eye Care", "💊 Wellness Support"]
    )

    # =========================================================
    # STRESS RELIEF
    # =========================================================
    with tab1:

        st.image(
            "https://images.unsplash.com/photo-1506126613408-eca07ce68773",
            width=700,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="
            background:rgba(255,255,255,0.04);
            padding:18px;
            border-radius:16px;
            border:1px solid rgba(255,255,255,0.08);
            margin-bottom:18px;
            ">
            <h3 style='margin-top:0px;'>🧘 AI Stress Relief</h3>
            <p style='opacity:0.8; margin-bottom:0px;'>
            Get personalized recovery & stress management suggestions.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🧘 Generate Relaxation Plan", use_container_width=True):
            profile = st.session_state.get("profile_data", "No profile")
            result = stress_relief(profile)
            st.session_state["stress_result"] = result

        if "stress_result" in st.session_state:

            st.markdown(
                "<h3 style='margin-bottom:10px;'>🌿 Your Recovery Plan</h3>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="
                background:rgba(255,255,255,0.04);
                padding:18px;
                border-radius:16px;
                border:1px solid rgba(255,255,255,0.08);
                ">
                {st.session_state["stress_result"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================
    # EYE CARE
    # =========================================================
    with tab2:

        st.image(
            "https://images.unsplash.com/photo-1516321318423-f06f85e504b3",
            width=700,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="
            background:rgba(255,255,255,0.04);
            padding:18px;
            border-radius:16px;
            border:1px solid rgba(255,255,255,0.08);
            margin-bottom:18px;
            ">
            <h3 style='margin-top:0px;'>👁️ Daily Eye Care</h3>
            <ul style='margin-bottom:0px;'>
                <li>Follow the 20-20-20 rule</li>
                <li>Blink frequently</li>
                <li>Reduce screen brightness</li>
                <li>Use proper lighting</li>
                <li>Sleep 7–8 hours</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("👁️ Get Personalized Eye Tips", use_container_width=True):
            profile = st.session_state.get("profile_data", {})
            result = generate_eye_care(profile)
            st.session_state["eye_tips"] = result

        if "eye_tips" in st.session_state:

            st.success("👁️ Personalized eye-care recommendations generated")
            st.markdown(
                f"""
                <div style="
                background:rgba(255,255,255,0.04);
                padding:18px;
                border-radius:16px;
                border:1px solid rgba(255,255,255,0.08);
                ">
                {st.session_state["eye_tips"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================
    # WELLNESS SUPPORT
    # =========================================================
    with tab3:

        st.image(
            "https://images.unsplash.com/photo-1498837167922-ddd27525d352",
            width=700,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="
            background:rgba(255,255,255,0.04);
            padding:18px;
            border-radius:16px;
            border:1px solid rgba(255,255,255,0.08);
            ">
            <h3 style='margin-top:0px;'>💊 General Wellness Support</h3>
            <p style='opacity:0.8;'>Non-medical wellness suggestions for recovery & daily health.</p>
            <ul>
                <li>Magnesium → supports relaxation</li>
                <li>Herbal tea → supports stress relief</li>
                <li>Electrolytes → supports hydration</li>
                <li>Vitamin B12 → supports energy</li>
                <li>Omega-3 → supports brain health</li>
            </ul>
            <p style='opacity:0.7; margin-bottom:0px;'>
            ⚠️ Always consult a professional before supplements
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
