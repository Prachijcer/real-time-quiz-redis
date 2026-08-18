import streamlit as st
from utils.ui import render_page_header
from services.quiz_service import quiz_service

def render():
    render_page_header("Available Quizzes", "Select a quiz below to test your skills in real time", "📚")

    user = st.session_state.get("user")
    username = user["username"] if user else None

    quizzes = quiz_service.get_all_quizzes()

    if not quizzes:
        st.info("No quizzes are currently available.")
        return

    cols = st.columns(2)
    for idx, q in enumerate(quizzes):
        with cols[idx % 2]:
            questions = quiz_service.get_questions_for_quiz(q["id"])
            q_count = len(questions)
            has_attempted = quiz_service.has_user_attempted(username, q["id"]) if username else False

            st.markdown(f"""
                <div class="quiz-card">
                    <div style="display:flex; justify-shadow:space-between; align-items:center; margin-bottom:10px;">
                        <h3 style="color:#818cf8; margin:0;">{q['title']}</h3>
                        <span class="badge {'badge-success' if has_attempted else 'badge-info'}">
                            {'Completed' if has_attempted else 'Available'}
                        </span>
                    </div>
                    <p style="color:#cbd5e1; font-size:0.95rem;">{q['description']}</p>
                    <div style="display:flex; gap:15px; color:#94a3b8; font-size:0.85rem; margin-top:15px; margin-bottom:15px;">
                        <span>⏱️ Duration: <b>{q['duration_minutes']} min</b></span>
                        <span>❓ Questions: <b>{q_count}</b></span>
                        <span>🎯 Pass: <b>{q.get('pass_percentage', 60)}%</b></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if not username:
                if st.button(f"Log In to Take {q['title']}", key=f"btn_login_{q['id']}", use_container_width=True):
                    st.session_state.page = "Login"
                    st.rerun()
            elif has_attempted:
                st.button(f"✅ Already Completed", key=f"btn_done_{q['id']}", disabled=True, use_container_width=True)
            else:
                if st.button(f"▶️ Start Quiz Now", key=f"btn_start_{q['id']}", type="primary", use_container_width=True):
                    res = quiz_service.start_quiz_session(username, q["id"])
                    if res["success"]:
                        st.session_state.active_quiz_id = q["id"]
                        st.session_state.page = "Quiz Page"
                        st.rerun()
                    else:
                        st.error(res["message"])
