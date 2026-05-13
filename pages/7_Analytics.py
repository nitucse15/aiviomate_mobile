import streamlit as st
import pandas as pd
import plotly.express as px
import random
import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Analytics",
    layout="centered",
)

# =========================
# CUSTOM STYLING
# =========================
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
    st.switch_page("app_mobile.py")

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
