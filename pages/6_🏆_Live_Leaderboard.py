import streamlit as st
import pandas as pd
from services.redis_service import redis_service

st.set_page_config(page_title="Live Leaderboard - Redis Quiz", page_icon="🏆", layout="wide")

user = st.session_state.get("user")

# Sidebar Navigation
if st.sidebar.button("🏠 Home", use_container_width=True):
    st.switch_page("Home.py")

if user:
    if user["role"] == "admin":
        if st.sidebar.button("⚙️ Admin Dashboard", use_container_width=True):
            st.switch_page("pages/7_⚙_Admin_Dashboard.py")
    else:
        if st.sidebar.button("👤 Student Dashboard", use_container_width=True):
            st.switch_page("pages/3_👤_Student_Dashboard.py")

    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.user = None
        st.session_state.auth_role = None
        st.switch_page("Home.py")

st.markdown("""
    <div style="border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; margin-bottom: 20px;">
        <h1 style="font-size: 2rem; color: #2dd4bf; margin: 0;">🏆 Real-Time Live Leaderboard</h1>
        <p style="color: #94a3b8; font-size: 0.95rem;">Rankings are computed live from Redis Sorted Sets (ZSET) on localhost:6379</p>
    </div>
""", unsafe_allow_html=True)

quizzes = st.session_state.get("quizzes", [])
quiz_options = {"overall": "🏆 Overall Leaderboard"}
for q in quizzes:
    quiz_options[q["id"]] = f"📘 {q['title']}"

selected_cat = st.selectbox(
    "Select Leaderboard Category:",
    options=list(quiz_options.keys()),
    format_func=lambda x: quiz_options[x]
)

raw_lb = redis_service.get_leaderboard(selected_cat)

if not raw_lb:
    st.info("No rankings recorded in Redis for this category yet. Take a quiz to appear here!")
else:
    table_data = []
    for rank_idx, (username, score) in enumerate(raw_lb, 1):
        user_info = redis_service.get_user(username)
        name = user_info.get("name", username.capitalize())
        medal = "🥇 " if rank_idx == 1 else ("🥈 " if rank_idx == 2 else ("🥉 " if rank_idx == 3 else ""))

        table_data.append({
            "Rank": f"#{rank_idx}",
            "Student": f"{medal}{name} (@{username})",
            "Score": f"{int(score)}/10" if score <= 10 else f"{int(score)} pts"
        })

    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
