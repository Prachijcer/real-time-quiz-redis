import streamlit as st
from utils.ui import render_page_header, render_stat_card
from services.quiz_service import quiz_service
from services.redis_service import redis_service

def render():
    attempt = st.session_state.get("last_attempt")
    user = st.session_state.get("user")

    if not attempt and user:
        # Fallback to latest attempt
        user_attempts = quiz_service.get_user_attempts(user["username"])
        if user_attempts:
            attempt = user_attempts[-1]

    if not attempt:
        st.info("No quiz results available.")
        if st.button("Browse Quizzes"):
            st.session_state.page = "Available Quizzes"
            st.rerun()
        return

    quiz = quiz_service.get_quiz_by_id(attempt["quiz_id"])
    title = quiz["title"] if quiz else attempt["quiz_id"]
    username = attempt["username"]

    # Fetch live rank from Redis Sorted Set
    redis_rank = redis_service.get_user_rank(attempt["quiz_id"], username)
    redis_score = redis_service.get_user_score(attempt["quiz_id"], username)

    render_page_header(f"Quiz Results: {title}", f"Submitted by @{username} on {attempt['submitted_at']}", "📊")

    is_passed = attempt["percentage"] >= 60

    # Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card("Score Achieved", f"{attempt['score']} / {attempt['total_questions']}", "#818cf8")
    with c2:
        render_stat_card("Percentage", f"{attempt['percentage']}%", "#34d399" if is_passed else "#ef4444")
    with c3:
        render_stat_card("Redis Live Rank", f"#{redis_rank}" if redis_rank else "N/A", "#c084fc")
    with c4:
        render_stat_card("Result Status", "PASSED 🎉" if is_passed else "FAILED ❌", "#34d399" if is_passed else "#ef4444")

    st.markdown("<br>", unsafe_allow_html=True)

    # Action buttons
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🏆 View Live Leaderboard", use_container_width=True, type="primary"):
            st.session_state.page = "Live Leaderboard"
            st.rerun()
    with col_b:
        if st.button("👤 Return to Dashboard", use_container_width=True):
            st.session_state.page = "Student Dashboard"
            st.rerun()

    st.markdown("---")

    # Detailed Question Review
    st.subheader("🔍 Question Breakdown & Explanations")
    questions = quiz_service.get_questions_for_quiz(attempt["quiz_id"])
    student_ans = attempt.get("answers", {})

    for idx, q in enumerate(questions, 1):
        user_choice = student_ans.get(q["id"], "No Answer")
        correct_choice = q["correct_answer"]
        is_correct = (user_choice == correct_choice)

        status_icon = "✅" if is_correct else "❌"
        border_color = "#34d399" if is_correct else "#ef4444"

        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.6); border-left: 4px solid {border_color};
                        padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h5 style="color:#f8fafc; margin:0;">{status_icon} Question {idx}: {q['question']}</h5>
                </div>
                <div style="margin-top: 8px; font-size:0.9rem; color:#cbd5e1;">
                    <span>Your Answer: <b style="color: {'#4ade80' if is_correct else '#f87171'};">{user_choice}</b></span><br>
                    <span>Correct Answer: <b style="color: #4ade80;">{correct_choice}</b></span>
                </div>
            </div>
        """, unsafe_allow_html=True)
