import time
import streamlit as st
from utils.ui import render_page_header
from services.quiz_service import quiz_service
from services.redis_service import redis_service

def render():
    user = st.session_state.get("user")
    quiz_id = st.session_state.get("active_quiz_id")

    if not user or not quiz_id:
        st.warning("No active quiz session found.")
        if st.button("Return to Available Quizzes"):
            st.session_state.page = "Available Quizzes"
            st.rerun()
        return

    username = user["username"]
    quiz = quiz_service.get_quiz_by_id(quiz_id)
    questions = quiz_service.get_questions_for_quiz(quiz_id)

    if not quiz or not questions:
        st.error("Quiz or question data is missing.")
        return

    # Check if duplicate submission
    if quiz_service.has_user_attempted(username, quiz_id):
        st.warning("You have already submitted this quiz!")
        if st.button("View Results"):
            st.session_state.page = "Result Page"
            st.rerun()
        return

    # Fetch active session state from Redis Hash
    session_data = redis_service.get_user_session(username)
    start_time = float(session_data.get("start_time", time.time()))
    duration_seconds = quiz["duration_minutes"] * 60

    elapsed_seconds = int(time.time() - start_time)
    remaining_seconds = max(0, duration_seconds - elapsed_seconds)

    render_page_header(f"Quiz: {quiz['title']}", f"Questions: {len(questions)} | Duration: {quiz['duration_minutes']} mins", "⏱️")

    # Countdown Timer & Progress header
    col_progress, col_timer = st.columns([3, 1])

    with col_timer:
        mins, secs = divmod(remaining_seconds, 60)
        st.markdown(f"""
            <div class="timer-box">
                ⏱️ {mins:02d}:{secs:02d}
            </div>
        """, unsafe_allow_html=True)

    if remaining_seconds <= 0:
        st.error("⏰ Time's up! Automatically submitting your answers...")
        _handle_submission(username, quiz_id, elapsed_seconds)
        return

    # Initialize answers dict in session state
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}

    with col_progress:
        answered_count = len([q for q in questions if q["id"] in st.session_state.quiz_answers and st.session_state.quiz_answers[q["id"]]])
        st.progress(answered_count / len(questions), text=f"Progress: {answered_count} of {len(questions)} answered")

    st.markdown("<br>", unsafe_allow_html=True)

    # Render Question Forms
    with st.form("quiz_questions_form"):
        for idx, q in enumerate(questions, 1):
            st.markdown(f"""
                <div style="background: rgba(30, 41, 59, 0.5); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 15px;">
                    <h4 style="color:#818cf8; margin-top:0;">Question {idx} of {len(questions)}</h4>
                    <p style="font-size:1.1rem; font-weight:600; color:#f8fafc;">{q['question']}</p>
                </div>
            """, unsafe_allow_html=True)

            selected = st.radio(
                label=f"Select your answer for Question {idx}:",
                options=q["options"],
                key=f"q_radio_{q['id']}",
                index=None if q["id"] not in st.session_state.quiz_answers else (
                    q["options"].index(st.session_state.quiz_answers[q["id"]])
                    if st.session_state.quiz_answers[q["id"]] in q["options"] else None
                )
            )
            if selected:
                st.session_state.quiz_answers[q["id"]] = selected

        st.markdown("<br>", unsafe_allow_html=True)
        submit_clicked = st.form_submit_button("🏁 Submit Quiz", type="primary", use_container_width=True)

        if submit_clicked:
            _handle_submission(username, quiz_id, elapsed_seconds)

def _handle_submission(username: str, quiz_id: str, elapsed_seconds: int):
    answers = st.session_state.get("quiz_answers", {})
    res = quiz_service.submit_quiz(username, quiz_id, answers, elapsed_seconds)
    if res["success"]:
        st.session_state.last_attempt = res["attempt"]
        st.session_state.active_quiz_id = None
        st.session_state.quiz_answers = {}
        st.session_state.page = "Result Page"
        st.rerun()
    else:
        st.error(res["message"])
