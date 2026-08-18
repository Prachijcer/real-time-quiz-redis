import streamlit as st
import pandas as pd
from utils.ui import render_page_header, render_stat_card
from services.quiz_service import quiz_service
from services.redis_service import redis_service
from services.auth_service import auth_service

def render():
    render_page_header("Live Real-Time Leaderboard", "Scores & rankings fetched directly from Redis Sorted Sets (ZSET)", "🏆")

    # Quiz Filter selector
    quizzes = quiz_service.get_all_quizzes()
    quiz_options = {"overall": "🏆 Overall Leaderboard"}
    for q in quizzes:
        quiz_options[q["id"]] = f"📘 {q['title']}"

    selected_quiz_id = st.selectbox(
        "Select Quiz Leaderboard Category:",
        options=list(quiz_options.keys()),
        format_func=lambda x: quiz_options[x]
    )

    # Current Logged-in User Rank Spotlight
    user = st.session_state.get("user")
    current_username = user["username"] if user else None

    if current_username:
        user_rank = redis_service.get_user_rank(selected_quiz_id, current_username)
        user_score = redis_service.get_user_score(selected_quiz_id, current_username)

        c1, c2, c3 = st.columns(3)
        with c1:
            render_stat_card("Logged-in Student", f"@{current_username}", "#6366f1")
        with c2:
            render_stat_card("Your Rank in Redis", f"#{user_rank}" if user_rank else "Unranked", "#c084fc")
        with c3:
            render_stat_card("Your Score in Redis", f"{user_score or 0} pts", "#34d399")

        st.markdown("<br>", unsafe_allow_html=True)

    # Fetch Leaderboard directly from Redis Sorted Set (ZREVRANGE)
    raw_leaderboard = redis_service.get_leaderboard(selected_quiz_id, top_n=100)

    # Status banner indicating Redis source
    status_info = redis_service.get_status()
    mode_text = "Standard Redis Server (localhost:6379)" if not status_info["is_fake"] else "Embedded Redis Engine (fakeredis)"
    st.caption(f"⚡ *Live Data Source: {mode_text} | Redis Key: `leaderboard:{selected_quiz_id}`*")

    if not raw_leaderboard:
        st.info("No scores recorded in Redis for this leaderboard category yet.")
        return

    table_data = []
    for rank_idx, (username, score) in enumerate(raw_leaderboard, 1):
        user_obj = auth_service.get_user(username)
        full_name = user_obj["name"] if user_obj else username

        # Rank Medals
        medal = ""
        if rank_idx == 1:
            medal = "🥇 "
        elif rank_idx == 2:
            medal = "🥈 "
        elif rank_idx == 3:
            medal = "🥉 "

        is_current = (username == current_username)
        student_display = f"{medal}{full_name} (@{username})"
        if is_current:
            student_display += " ⭐ (YOU)"

        table_data.append({
            "Rank": f"#{rank_idx}",
            "Student": student_display,
            "Score": f"{score:.0f} pts" if score.is_integer() else f"{score:.1f} pts"
        })

    df = pd.DataFrame(table_data)

    # Render Leaderboard Table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.TextColumn("Rank", width="small"),
            "Student": st.column_config.TextColumn("Student Name & Handle", width="large"),
            "Score": st.column_config.TextColumn("Redis Score", width="medium")
        }
    )

    if st.button("🔄 Refresh Live Rankings"):
        st.rerun()
