import streamlit as st
import pandas as pd
from utils.ui import render_page_header, render_stat_card
from services.quiz_service import quiz_service
from services.redis_service import redis_service

def render():
    user = st.session_state.get("user")
    if not user or st.session_state.get("role") != "student":
        st.warning("Please log in as a student to access your dashboard.")
        if st.button("Go to Login"):
            st.session_state.page = "Login"
            st.rerun()
        return

    username = user["username"]
    render_page_header(f"Welcome, {user['name']}!", f"Student Dashboard (@{username})", "👤")

    # Fetch stats from Redis & attempts
    rank = redis_service.get_user_rank("overall", username)
    overall_score = redis_service.get_user_score("overall", username)
    user_attempts = quiz_service.get_user_attempts(username)

    total_attempts = len(user_attempts)
    avg_score = round(sum(a["score"] for a in user_attempts) / total_attempts, 2) if total_attempts > 0 else 0.0

    # Key Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card("Overall Rank", f"#{rank}" if rank else "Unranked", "#818cf8")
    with c2:
        render_stat_card("Total Score", f"{overall_score or 0} pts", "#c084fc")
    with c3:
        render_stat_card("Quizzes Attempted", total_attempts, "#34d399")
    with c4:
        render_stat_card("Average Score", f"{avg_score} pts", "#fbbf24")

    st.markdown("<br>", unsafe_allow_html=True)

    # Action bar
    act1, act2 = st.columns(2)
    with act1:
        if st.button("📚 Browse Available Quizzes", use_container_width=True):
            st.session_state.page = "Available Quizzes"
            st.rerun()
    with act2:
        if st.button("🏆 Check Live Leaderboard", use_container_width=True):
            st.session_state.page = "Live Leaderboard"
            st.rerun()

    st.markdown("---")

    # Past Quiz Attempt History
    st.subheader("📋 Your Quiz Attempt History")
    if not user_attempts:
        st.info("You haven't attempted any quizzes yet. Click 'Browse Available Quizzes' to start!")
    else:
        history_data = []
        for a in reversed(user_attempts):
            quiz = quiz_service.get_quiz_by_id(a["quiz_id"])
            title = quiz["title"] if quiz else a["quiz_id"]
            history_data.append({
                "Quiz Title": title,
                "Score": f"{a['score']} / {a['total_questions']}",
                "Percentage": f"{a['percentage']}%",
                "Time Taken": f"{a['time_taken_seconds']}s",
                "Date Submitted": a["submitted_at"]
            })

        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
