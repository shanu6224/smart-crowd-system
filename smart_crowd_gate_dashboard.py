import streamlit as st
import numpy as np
from datetime import datetime

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(page_title="Smart Crowd Gate System", layout="centered")
st.title("🚦 Smart Crowd Management – 4 Gate System")

# -----------------------------
# DAY / NIGHT MODE
# -----------------------------
GREEN_LIMIT = 50
YELLOW_LIMIT = 100

hour = datetime.now().hour
if 6 <= hour < 18:
    time_mode = "☀ MORNING MODE"
    brightness = "Bright Signals"
else:
    time_mode = "🌙 NIGHT MODE"
    brightness = "Dim Signals"

st.subheader(f"{time_mode} | {brightness}")
st.info(
    f"System Time Mode: **{time_mode}** | "
    f"Green ≤ {GREEN_LIMIT}, Yellow ≤ {YELLOW_LIMIT}, Red > {YELLOW_LIMIT}"
)

# -----------------------------
# CHECK MOVIEPY
# -----------------------------
try:
    from moviepy.editor import VideoFileClip
    moviepy_available = True
except ModuleNotFoundError:
    st.warning("⚠ MoviePy not found. Video-based crowd estimation disabled.")
    moviepy_available = False

# -----------------------------
# LOAD VIDEO & CROWD ESTIMATION
# -----------------------------
if moviepy_available:
    video_path = "crowd.mp4"
    st.video(video_path)

    @st.cache_data
    def estimate_crowd(video_path):
        clip = VideoFileClip(video_path).subclip(0, 5)
        frames = list(clip.iter_frames(fps=1))

        densities = []
        for frame in frames:
            gray = np.mean(frame, axis=2)
            density = np.std(gray)
            densities.append(density)

        avg_density = np.mean(densities)
        crowd_count = int(avg_density * 0.8)  # Prototype logic
        return crowd_count

    crowd_count_estimated = estimate_crowd(video_path)
else:
    # Default crowd count if MoviePy is not available
    crowd_count_estimated = 50

# -----------------------------
# CROWD SLIDER
# -----------------------------
crowd_count = st.slider(
    "👥 Adjust/Simulate Crowd Count",
    min_value=0,
    max_value=200,
    value=crowd_count_estimated,
    step=1
)

# -----------------------------
# GATE SIGNAL LOGIC
# -----------------------------
GREEN = 25
YELLOW = 40

def gate_status(count):
    """Return signal, action, and color code"""
    if count <= GREEN:
        return "🟢 GREEN", "➡ IN OPEN | ⬅ OUT OPEN", "green"
    elif count <= YELLOW:
        return "🟡 YELLOW", "➡ IN SLOW | ⬅ OUT OPEN", "yellow"
    else:
        return "🔴 RED", "❌ IN BLOCKED | ⬅ OUT ONLY", "red"

# -----------------------------
# DISTRIBUTE CROWD TO 4 GATES
# -----------------------------
gate_loads = [
    int(crowd_count * 0.35),
    int(crowd_count * 0.25),
    int(crowd_count * 0.20),
    int(crowd_count * 0.20),
]

gates = ["Gate 1", "Gate 2", "Gate 3", "Gate 4"]

st.markdown("---")
st.subheader("🚪 Gate Status & Control")

# Display each gate in columns
cols = st.columns(4)
for i, gate in enumerate(gates):
    count = gate_loads[i]
    signal, action, color = gate_status(count)
    
    with cols[i]:
        st.markdown(f"### {gate}")
        st.metric(label="Crowd Count", value=f"{count}")
        st.markdown(
            f"<div style='background-color:{color};padding:5px;"
            f"border-radius:5px;text-align:center;color:white;'>{signal}</div>",
            unsafe_allow_html=True,
        )
        st.write(f"Action: {action}")
        
        # Redirect logic
        if signal == "🔴 RED" and i < 3:
            st.warning(f"➡️ Redirect crowd to **{gates[i+1]}**")
        elif signal == "🔴 RED" and i == 3:
            st.error("🚫 All gates overloaded. Please wait outside.")

# -----------------------------
# SUMMARY
# -----------------------------
st.markdown("---")
st.success(f"📊 Estimated Total Crowd Count: **{crowd_count}**")
st.info("This is a software-based prototype for temples, annadhanam halls & mass gatherings.")
