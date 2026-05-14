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
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# =========================
# PAGE CONFIG (MUST BE FIRST)
# =========================
st.set_page_config(
    page_title="AIVioMate",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================
# ANALYTICS STATE
# =========================
if "show_analytics" not in st.session_state:
    st.session_state.show_analytics = False

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

/* =========================
APP BACKGROUND
========================= */

.stApp {
    background:
    linear-gradient(
        135deg,
        #0f172a,
        #111827
    );
    color: white;
}

/* MAIN CONTAINER */
.main .block-container {

    max-width: 1150px;

    padding-top: 1rem;

    padding-left: 1rem;
    padding-right: 1rem;
}

/* =========================
SIDEBAR
========================= */

section[data-testid="stSidebar"] {

    background:
    linear-gradient(
        180deg,
        #081028,
        #0b1736
    ) !important;

    border-right:
    1px solid rgba(255,255,255,0.05);

    transition:
    all 0.3s ease-in-out;
}

/* SIDEBAR CONTAINER */

section[data-testid="stSidebar"] .block-container {

    padding-top: 1rem !important;

    padding-left: 1rem !important;
    padding-right: 1rem !important;

    padding-bottom: 1rem !important;
}

/* ALL SIDEBAR TEXT */

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* =========================
MOBILE SIDEBAR
========================= */

@media (max-width: 768px) {

    section[data-testid="stSidebar"][aria-expanded="true"] {

        width: 82vw !important;
        min-width: 82vw !important;
    }

    .main .block-container {

        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
}

/* =========================
SIDEBAR LOGO
========================= */

.sidebar-logo {

    margin-bottom: 8px !important;
}

.sidebar-title {

    margin-bottom: 0px !important;
}

.sidebar-divider {

    margin-top: 14px !important;
    margin-bottom: 14px !important;

    opacity: 0.08;
}

/* =========================
RADIO GROUP
========================= */

section[data-testid="stSidebar"] .stRadio > div {

    background: transparent !important;

    border: none !important;

    padding: 0 !important;
}

/* RADIO GAP */

section[data-testid="stSidebar"] div[role="radiogroup"] {

    gap: 10px;
}

/* BUTTON STYLE */

section[data-testid="stSidebar"] label[data-baseweb="radio"] {

    width: 100% !important;

    min-height: 44px !important;

    display: flex !important;

    align-items: center !important;

    padding:
    8px 14px !important;

    border-radius: 18px !important;

    background:
linear-gradient(
    90deg,
    rgba(91,95,239,0.55),
    rgba(139,92,246,0.55)
);

    border:
    1px solid rgba(255,255,255,0.08);

    transition:
    all 0.25s ease;

    box-sizing:
    border-box !important;

    margin-bottom:
    10px !important;
}

/* ACTIVE PAGE */

section[data-testid="stSidebar"]
label[data-baseweb="radio"][aria-checked="true"] {

    background:
    linear-gradient(
        90deg,
        #5B5FEF,
        #8B5CF6
    ) !important;

    border:
    1px solid rgba(255,255,255,0.15) !important;

    box-shadow:
    0 6px 18px rgba(99,102,241,0.25);
}

/* HOVER */

section[data-testid="stSidebar"]
label[data-baseweb="radio"]:hover {

    background:
    linear-gradient(
        90deg,
        #5B5FEF,
        #8B5CF6
    );

    transform:
    scale(1.01);
}

/* TEXT */

section[data-testid="stSidebar"]
label[data-baseweb="radio"] span {

    color: white !important;

    font-size: 15px !important;

    font-weight: 600 !important;
}

/* RADIO DOT */

section[data-testid="stSidebar"]
input[type="radio"] {

    accent-color: #ffffff;
}

/* =========================
HEADINGS
========================= */

h1, h2, h3, h4, h5, h6, label {
    color: white !important;
}

/* =========================
BUTTONS
========================= */

.stButton > button {

    background:
    linear-gradient(
        90deg,
        #5B5FEF,
        #8B5CF6
    ) !important;

    color: white !important;

    border: none !important;

    border-radius: 14px !important;

    width: 100% !important;

    height: 52px !important;

    font-weight: 700 !important;

    font-size: 16px !important;

    transition:
    all 0.25s ease !important;

    opacity: 1 !important;

    visibility: visible !important;
}

/* BUTTON HOVER */

.stButton > button:hover {

    background:
    linear-gradient(
        90deg,
        #4F46E5,
        #7C3AED
    ) !important;

    transform:
    scale(1.01);
}

/* DOWNLOAD BUTTON */

div.stDownloadButton > button {

    background:
    linear-gradient(
        90deg,
        #6366f1,
        #8b5cf6
    ) !important;

    color: white !important;

    border-radius: 10px !important;

    border: none !important;

    font-weight: 600 !important;
}

/* =========================
INPUTS
========================= */

input,
textarea {

    background-color:
    #0e2a47 !important;

    color:
    white !important;

    border:
    1px solid rgba(255,255,255,0.2) !important;

    border-radius:
    12px !important;
}

input::placeholder,
textarea::placeholder {

    color:
    #aaa !important;
}

div[data-baseweb="input"] > div {

    background-color:
    #0e2a47 !important;

    border-radius:
    12px;
}

div[data-baseweb="input"] input:focus {

    outline: none !important;

    border:
    1px solid #6366f1 !important;
}

/* SELECT BOX */

div[data-baseweb="select"] > div {

    background-color:
    #0e2a47 !important;

    color:
    white !important;

    border-radius:
    10px;
}

/* =========================
CARDS
========================= */

.card {

    background:
    rgba(255,255,255,0.06);

    padding: 16px;

    border-radius: 14px;

    border:
    1px solid rgba(255,255,255,0.08);

    backdrop-filter:
    blur(8px);
}

/* =========================
IMAGES
========================= */

img {

    border-radius: 18px;

    object-fit: cover;
}

/* =========================
PROGRESS BAR
========================= */

.stProgress > div > div {

    background:
    linear-gradient(
        90deg,
        #22c55e,
        #4ade80
    );
}

/* =========================
CHAT BUBBLES
========================= */

.user-bubble {

    background:
    linear-gradient(
        90deg,
        #6366f1,
        #8b5cf6
    );

    padding:
    12px 16px;

    border-radius:
    18px 18px 4px 18px;

    color: white;

    margin: 10px 0;

    max-width: 75%;

    width: fit-content;

    margin-left: auto;

    font-size: 15px;

    line-height: 1.7;
}

.bot-bubble {

    background:
    rgba(255,255,255,0.08);

    padding: 16px;

    border-radius:
    18px 18px 18px 4px;

    color: white;

    margin: 10px 0;

    max-width: 85%;

    width: fit-content;

    line-height: 1.8;

    border:
    1px solid rgba(255,255,255,0.06);

    backdrop-filter:
    blur(10px);
}

/* LINKS */

.bot-bubble a {

    color: white !important;

    text-decoration: underline;
}

/* =========================
EXPANDERS
========================= */

.streamlit-expanderHeader {

    background:
    rgba(255,255,255,0.05) !important;

    color:
    white !important;

    border-radius:
    12px !important;

    border:
    1px solid rgba(255,255,255,0.08) !important;
}

.streamlit-expanderContent {

    background:
    rgba(255,255,255,0.03) !important;

    border-radius:
    0px 0px 12px 12px !important;

    color:
    white !important;
}

/* =========================
ALERTS
========================= */

div[data-testid="stAlert"] {
    color: white !important;
}

.stAlert p {
    color: white !important;
}

/* =========================
TEXT
========================= */

p {
    color: white !important;
}

details {
    color: white !important;
}

details p {
    color: white !important;
}

/* =========================
FILE UPLOADER
========================= */

div[data-testid="stFileUploader"] {

    background-color:
    transparent !important;
}

/* =========================
MOBILE RESPONSIVE
========================= */

@media (max-width: 768px) {

    h1 {
        font-size: 28px !important;
    }

    h2 {
        font-size: 24px !important;
    }

    h3 {
        font-size: 20px !important;
    }

    .stButton button {

        height: 42px;

        font-size: 14px;
    }

    .user-bubble,
    .bot-bubble {

        max-width: 95%;

        font-size: 14px;
    }
}

/* HIDE UNUSED */

.stat-card {
    display: none;
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

if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

# =========================
# SIDEBAR NAVIGATION
# =========================

with st.sidebar:

    st.image(LOGO_URL, width=110)

    st.markdown(
        """
        <h1 style="
        color:white;
        font-size:30px;
        margin-bottom:0px;
        ">
        ⚡ AIVioMate
        </h1>

        <p style="
        color:#9ca3af;
        margin-top:6px;
        font-size:15px;
        ">
        AI Wellness Companion
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    <div style="
    height:1px;
    background:rgba(255,255,255,0.08);
    margin:8px 0 8px 0;
    ">
    </div>
    """,
        unsafe_allow_html=True,
    )
    tabs = [
        "Profile",
        "Dashboard",
        "Workout",
        "Nutrition",
        "Coach",
        "Wellness",
    ]

    selected_page = st.radio(
        "",
        tabs,
        index=tabs.index(st.session_state.page),
        label_visibility="collapsed",
    )

    # =========================
    # PAGE CHANGE
    # =========================

    if selected_page != st.session_state.page:

        st.session_state.page = selected_page

        # AUTO CLOSE SIDEBAR
        st.session_state.show_sidebar = False

        st.rerun()

page = st.session_state.page

st.markdown(
    """
    <div style="
    color:#d1d5db;
    font-size:16px;
    margin-bottom:10px;
    font-weight:500;
    ">
    👉 Click <b>&gt;&gt; </b> to open menu • Select a page then tap outside menu
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<div style='height:12px'></div>",
    unsafe_allow_html=True,
)
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
background:rgba(99,102,241,0.10);
padding:20px;
border-radius:18px;
border:1px solid rgba(255,255,255,0.06);
margin-bottom:25px;
">

<h3 style="color:white;">
🚀 Welcome to AIVioMate
</h3>

<p style="
color:#d1d5db;
font-size:15px;
line-height:1.7;
margin-bottom:0;
">
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

<h4>👤 Step 1 — Complete Your Profile</h4>

Fill:

<ul>
    <li>Age</li>
    <li>Weight</li>
    <li>Fitness Goal</li>
    <li>Lifestyle</li>
    <li>Activity Level</li>
    <li>Illness</li>
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

<hr style="margin:18px 0; opacity:0.15;">

<h3>🧘 Wellness</h3>

Get wellness guidance for:

<ul>
    <li>Stress management</li>
    <li>Eye care tips</li>
    <li>Recovery support</li>
    <li>General wellness supplements</li>
    <li>Healthy lifestyle habits</li>
</ul>

<hr>

<h3>🤖 AI Coach</h3>

Ask questions anytime about:

<ul>
    <li>Fitness</li>
    <li>Recovery</li>
    <li>Nutrition</li>
    <li>Stress</li>
    <li>Wellness</li>
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
        <h3 style='margin-bottom:4px;'>👤 Your Profile</h3>
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

    # =========================
    # HEALTH CONDITIONS
    # =========================
    illness = st.text_input(
        "Health Conditions / Illness (Optional)",
        placeholder="Example: Diabetes, thyroid, heart condition, knee pain, asthma...",
    )

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
                "injury": injury,
                "illness": illness,
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
    if "show_analytics" not in st.session_state:
        st.session_state.show_analytics = False

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
            sleep = st.slider(
                "Sleep (hrs)",
                0,
                12,
                st.session_state.get("sleep", 6),
            )
            st.session_state.sleep = sleep

        with c2:
            stress = st.slider(
                "Stress",
                0,
                10,
                st.session_state.get("stress", 4),
            )
            st.session_state.stress = stress

        energy = st.slider(
            "Energy",
            0,
            10,
            st.session_state.get("energy", 6),
        )

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
font-size:12px;
font-weight:600;
margin-bottom:8px;
color:white;
text-align:center;
">
{label}
</div>
""",
                    unsafe_allow_html=True,
                )

                if st.button(
                    emoji,
                    key=f"mood_{i}",
                    use_container_width=True,
                ):
                    st.session_state.mood = label
                    st.session_state.mood_value = score_value
                    st.rerun()

        current_mood = st.session_state.get("mood", "Not Selected")

        st.caption(f"Current Mood: {current_mood}")

        st.markdown("<br>", unsafe_allow_html=True)

        # =========================
        # HYDRATION
        # =========================
        st.markdown("## 💧 Hydration")

        water = st.slider(
            "Daily Water Intake (glasses)",
            min_value=0,
            max_value=12,
            value=st.session_state.get("water", 0),
        )

        st.session_state.water = water

        st.markdown(
            f"""
<div style="
font-size:20px;
font-weight:600;
margin-top:8px;
margin-bottom:20px;
color:white;
">
{water} / 12 glasses
</div>
""",
            unsafe_allow_html=True,
        )

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

        mood_value = mood_map.get(
            st.session_state.get("mood"),
            0,
        )

        has_inputs = any(
            [
                sleep > 0,
                stress > 0,
                energy > 0,
                st.session_state.water > 0,
                mood_value > 0,
            ]
        )

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

            score = min(
                int(sum(values) / len(values)),
                100,
            )

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
                    marker=dict(
                        colors=[
                            color,
                            "#1f2937",
                        ]
                    ),
                )
            ]
        )

        fig.update_layout(
            width=240,
            height=240,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(
                t=0,
                b=0,
                l=0,
                r=0,
            ),
            showlegend=False,
            annotations=[
                dict(
                    text=f"<b>{score}</b><br>{label}",
                    x=0.5,
                    y=0.5,
                    font=dict(
                        size=26,
                        color="white",
                    ),
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

        st.markdown("<br>", unsafe_allow_html=True)

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

        st.markdown("<br>", unsafe_allow_html=True)

        # =========================
        # BUTTONS
        # =========================
        if st.button(
            "📈 Open Detailed Analytics",
            use_container_width=True,
        ):
            st.session_state.show_analytics = True
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

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
    # ANALYTICS VIEW
    # =====================================================
    else:

        if st.button(
            "⬅ Back to Dashboard",
            use_container_width=True,
        ):
            st.session_state.show_analytics = False
            st.rerun()

        st.markdown("## 📊 Performance Insights")

        st.caption("Monitor your wellness trends over time.")

        # =========================
        # ANALYTICS DATA
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

        df = pd.DataFrame(st.session_state.analytics_data)

        df["date"] = pd.to_datetime(df["date"])

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

    # =========================
    # HERO CARD
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
🔥 Personalized Fitness Guidance
</h3>

<p style="
color:#d1d5db;
font-size:15px;
line-height:1.7;
margin-bottom:0;
">
Generate personalized AI-powered workout plans based on your goals, fitness level and recovery.
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
            "https://images.unsplash.com/photo-1599058917212-d750089bc07e",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # GENERATE WORKOUT
    # =========================

    st.info("👉 Complete your Profile for highly personalized workout recommendations")

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
            "## 🏋️ Your Workout Plan",
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
padding:20px;
border-radius:18px;
border:1px solid rgba(255,255,255,0.08);
line-height:1.8;
">
{clean_text}
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # ZUMBA SECTION
    # =========================
    st.markdown(
        """
<div style="
background:rgba(99,102,241,0.10);
padding:20px;
border-radius:18px;
border:1px solid rgba(255,255,255,0.06);
margin-bottom:22px;
">

<h3 style='margin-top:0px; color:white;'>
💃 Dance & Zumba Workouts
</h3>

<p style='color:#d1d5db; line-height:1.7; margin-bottom:0px;'>
Looking for something fun, energetic and beginner-friendly?
Try dance-based cardio and zumba fitness routines.
</p>

</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("💃 Show Zumba Workout", use_container_width=True):

        result = generate_zumba()

        st.markdown(
            "## 💃 Zumba Workout Plan",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
<div style="
background:rgba(255,255,255,0.04);
padding:20px;
border-radius:18px;
border:1px solid rgba(255,255,255,0.08);
line-height:1.8;
">
{result}
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # WORKOUT HISTORY
    # =========================
    st.markdown(
        "### 📚 Workout History",
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

    # =========================
    # HERO CARD
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
🥗 Smart Nutrition Guidance
</h3>

<p style="
color:#d1d5db;
font-size:15px;
line-height:1.7;
margin-bottom:0;
">
Personalized nutrition plans designed for your fitness goals, lifestyle, illness and skin health.
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
            "https://libapps-au.s3-ap-southeast-2.amazonaws.com/accounts/97668/images/teadergrafik_nutritions.jpg",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # NUTRITION FORM
    # =========================
    st.markdown("### 🥙 Nutrition Preferences")

    st.markdown(
        """
    <div style="
    background:rgba(255,255,255,0.04);
    padding:18px;
    border-radius:16px;
    margin-bottom:22px;
    border:1px solid rgba(255,255,255,0.08);
    ">

    <p style="
    color:#d1d5db;
    font-size:15px;
    line-height:1.7;
    margin-bottom:0;
    ">
    ✨ Please complete your profile and select your cuisine, food type and skin preferences below
    for smarter and more personalized meal recommendations.
    </p>

    </div>
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
        "### ✨ Skin Preferences",
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

        required_fields = ["age", "weight", "goal", "level", "illness"]

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
                final_profile,
                progress,
                cuisine,
                food_type,
                skin_type,
                skin_goal,
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
            "## 🍽️ Your Nutrition Plan",
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
padding:20px;
border-radius:18px;
border:1px solid rgba(255,255,255,0.08);
line-height:1.8;
">
{clean_text}
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # NUTRITION HISTORY
    # =========================
    st.markdown(
        "### 📚 Nutrition History",
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

    import re
    from difflib import get_close_matches

    # =========================
    # SESSION STATES
    # =========================
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "recent_chats" not in st.session_state:
        st.session_state.recent_chats = []

    # =========================
    # HERO CARD
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
🤖 Your Personal Coach
</h3>

<p style="
color:#d1d5db;
font-size:15px;
line-height:1.7;
margin-bottom:0;
">
Your AI companion for workouts, nutrition, recovery & wellness guidance.
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
            "https://coachvox.ai/wp-content/uploads/2023/04/AI-enhanced-coaching.jpg",
            use_container_width=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # QUICK SUGGESTIONS
    # =========================
    st.markdown(
        """
        <h2 style="
        color:white;
        margin-bottom:18px;
        font-weight:700;
        ">
        💡 Quick Suggestions
        </h2>
        """,
        unsafe_allow_html=True,
    )

    suggestions = [
        "Give me a workout for fat loss",
        "Easy high-protein breakfast ideas",
        "How to reduce stress quickly",
    ]

    cols = st.columns(3)

    for idx, q in enumerate(suggestions):

        with cols[idx]:

            if st.button(
                q,
                use_container_width=True,
                key=f"suggestion_{idx}",
            ):

                profile = get_user_profile()

                enhanced_query = f"""
                {q}

                IMPORTANT:
                - Fix typos automatically
                - Respond naturally
                - If user asks for videos, provide YouTube links
                """

                reply = coach_reply(enhanced_query, profile)

                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": q,
                    }
                )

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": reply,
                    }
                )

                st.session_state.recent_chats.insert(0, q)

                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # CHAT DISPLAY
    # =========================
    for msg in st.session_state.chat_history:

        if msg["role"] == "user":

            st.markdown(
                f"""
                <div style="
                display:flex;
                justify-content:flex-end;
                margin-bottom:14px;
                ">
                    <div style="
                    background:linear-gradient(135deg,#5B5FFB,#8B5CF6);
                    color:white;
                    padding:14px 18px;
                    border-radius:18px 18px 4px 18px;
                    max-width:75%;
                    font-size:15px;
                    font-weight:500;
                    box-shadow:0 4px 12px rgba(0,0,0,0.18);
                    ">
                    {msg["content"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            reply = msg["content"]

            # =========================
            # VIDEO LINKS
            # =========================
            if "video" in reply.lower() or "youtube" in reply.lower():

                urls = re.findall(r"(https?://[^\s]+)", reply)

                for url in urls:
                    reply = reply.replace(
                        url,
                        f"""
    <a href="{url}" 
    target="_blank" 
    style="
    color:#FFFFFF !important;
    text-decoration:underline !important;
    font-weight:500;
    ">
    {url}
    </a>
    """,
                    )

            st.markdown(
                f"""
                <div style="
                display:flex;
                justify-content:flex-start;
                margin-bottom:18px;
                ">
                    <div style="
                    background:rgba(255,255,255,0.05);
                    padding:18px;
                    border-radius:18px 18px 18px 4px;
                    max-width:85%;
                    line-height:1.9;
                    border:1px solid rgba(255,255,255,0.06);
                    font-size:15px;
                    box-shadow:0 4px 12px rgba(0,0,0,0.18);
                    color:white;
                    ">
                    {reply}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================
    # INPUT FORM
    # =========================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
    <style>

    div.stButton > button:first-child,
    div[data-testid="stFormSubmitButton"] button {

        background: linear-gradient(135deg, #5B5FFB, #8B5CF6) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        height: 52px !important;
        transition: 0.3s ease-in-out !important;
    }

    div.stButton > button:first-child:hover,
    div[data-testid="stFormSubmitButton"] button:hover {

        background: linear-gradient(135deg, #6366F1, #A855F7) !important;
        color: white !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(139,92,246,0.35);
    }

    </style>
    """,
        unsafe_allow_html=True,
    )

    with st.form("coach_form", clear_on_submit=True):

        user_input = st.text_input(
            "Ask your coach...",
            placeholder="Ask about workouts, recipes, videos, recovery...",
            label_visibility="visible",
        )

        submitted = st.form_submit_button(
            "🚀 Get Guidance",
            use_container_width=True,
        )
    # =========================
    # PROCESS INPUT
    # =========================
    if submitted and user_input.strip():

        profile = get_user_profile()

        enhanced_query = f"""
        {user_input}

        IMPORTANT INSTRUCTIONS:

        - Correct spelling mistakes automatically
        - Understand typo errors naturally
        - Reply like ChatGPT

        - If the user asks for:
            workout videos
            yoga videos
            recipe videos
            HIIT videos
            gym tutorials

        THEN provide 3 clickable YouTube links.

        Example:
        https://www.youtube.com/results?search_query=10+minute+hiit+workout

        Keep answers practical and concise.
        """

        reply = coach_reply(enhanced_query, profile)

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": reply,
            }
        )

        st.session_state.recent_chats.insert(0, user_input)

        st.rerun()

    # =========================
    # RECENT CHATS
    # =========================
    if st.session_state.recent_chats:

        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown(
            """
            <h2 style="
            color:white;
            font-weight:800;
            margin-bottom:20px;
            ">
            🕘 Recent Chats
            </h2>
            """,
            unsafe_allow_html=True,
        )

        unique_recent = []

        for chat in st.session_state.recent_chats:
            if chat not in unique_recent:
                unique_recent.append(chat)

        for idx, chat in enumerate(unique_recent[:6]):

            with st.expander(
                f"💬 {chat[:55]}...",
                expanded=False,
            ):
                st.markdown(
                    f"""
                    <div style="
                    color:white;
                    line-height:1.8;
                    font-size:15px;
                    ">
                    {chat}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
# =========================
# WELLNESS PAGE
# =========================
elif page == "Wellness":

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
🌿 Wellness & Recovery
</h3>

<p style="
color:#d1d5db;
font-size:15px;
line-height:1.7;
margin-bottom:0;
">
Improve recovery, reduce stress and build
        healthier daily wellness habits.
</p>

</div>
""",
        unsafe_allow_html=True,
    )
    # =========================
    # TABS
    # =========================
    tab1, tab2, tab3 = st.tabs(
        [
            "🧘 Stress Relief",
            "👁️ Eye Care",
            "💊 Wellness Support",
        ]
    )

    # =====================================================
    # STRESS RELIEF TAB
    # =====================================================
    with tab1:

        # =========================
        # CENTER IMAGE
        # =========================
        left, center, right = st.columns([1, 2.2, 1])

        with center:
            st.image(
                "https://images.unsplash.com/photo-1506126613408-eca07ce68773",
                use_container_width=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # =========================
        # CONTENT CARD
        # =========================
        st.markdown(
            """
            <div style="
            background:rgba(255,255,255,0.04);
            padding:20px;
            border-radius:18px;
            border:1px solid rgba(255,255,255,0.08);
            margin-bottom:18px;
            ">

            <h3 style="
            color:white;
            margin-top:0;
            ">
            🧘 Stress Relief & Recovery
            </h3>

            <p style="
            color:#d1d5db;
            line-height:1.8;
            margin-bottom:0;
            ">
            Improve focus, calm your mind and recover better
            with breathing exercises and mindfulness guidance.
            </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🧘 Generate Relaxation Tips",
            use_container_width=True,
        ):

            profile = st.session_state.get("profile_data", {})
            result = stress_relief(profile)

            st.session_state["stress_result"] = result

        if "stress_result" in st.session_state:

            st.markdown(
                """
                <h2 style="
                margin-bottom:12px;
                color:white;
                ">
                🌿 Your Wellness Guidance
                </h2>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div style="
                background:rgba(255,255,255,0.04);
                padding:22px;
                border-radius:18px;
                border:1px solid rgba(255,255,255,0.08);
                color:white;
                line-height:1.8;
                ">
                {st.session_state["stress_result"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =====================================================
    # EYE CARE TAB
    # =====================================================
    with tab2:

        # =========================
        # CENTER IMAGE
        # =========================
        left, center, right = st.columns([1, 2.2, 1])

        with center:
            st.image(
                "https://images.unsplash.com/photo-1516321318423-f06f85e504b3",
                use_container_width=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="
            background:rgba(255,255,255,0.04);
            padding:20px;
            border-radius:18px;
            border:1px solid rgba(255,255,255,0.08);
            margin-bottom:18px;
            ">

            <h3 style="
            color:white;
            margin-top:0;
            ">
            👁️ Eye Wellness
            </h3>

            <p style="
            color:#d1d5db;
            line-height:1.8;
            ">
            Reduce digital eye strain and improve visual comfort
            with healthier screen habits and recovery routines.
            </p>

            <ul style="
            color:#d1d5db;
            line-height:1.9;
            margin-bottom:0;
            ">
            <li>Follow the 20-20-20 rule</li>
            <li>Reduce screen brightness</li>
            <li>Improve room lighting</li>
            <li>Blink frequently</li>
            <li>Prioritize quality sleep</li>
            </ul>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "👁️ Get Eye Care Tips",
            use_container_width=True,
        ):

            profile = st.session_state.get("profile_data", {})
            result = generate_eye_care(profile)

            st.session_state["eye_tips"] = result

        if "eye_tips" in st.session_state:

            st.markdown(
                """
                <h2 style="
                margin-bottom:12px;
                color:white;
                ">
                👁️ Personalized Eye Care
                </h2>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div style="
                background:rgba(255,255,255,0.04);
                padding:22px;
                border-radius:18px;
                border:1px solid rgba(255,255,255,0.08);
                color:white;
                line-height:1.8;
                ">
                {st.session_state["eye_tips"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =====================================================
    # WELLNESS SUPPORT TAB
    # =====================================================
    with tab3:

        # =========================
        # CENTER IMAGE
        # =========================
        left, center, right = st.columns([1, 2.2, 1])

        with center:
            st.image(
                "https://images.unsplash.com/photo-1498837167922-ddd27525d352",
                use_container_width=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="
            background:rgba(255,255,255,0.04);
            padding:20px;
            border-radius:18px;
            border:1px solid rgba(255,255,255,0.08);
            ">

            <h3 style="
            color:white;
            margin-top:0;
            ">
            💊 Wellness Support
            </h3>

            <p style="
            color:#d1d5db;
            line-height:1.8;
            ">
            Build sustainable recovery habits that support
            better energy, sleep and overall wellbeing.
            </p>

            <ul style="
            color:#d1d5db;
            line-height:1.9;
            ">
            <li>Hydration & electrolytes</li>
            <li>Sleep recovery support</li>
            <li>Stress management habits</li>
            <li>Mindfulness & breathing</li>
            <li>Healthy recovery nutrition</li>
            </ul>

            <p style="
            color:#9ca3af;
            margin-bottom:0;
            ">
            ⚠️ Wellness suggestions are informational only
            and not medical advice.
            </p>

            </div>
            """,
            unsafe_allow_html=True,
        )
