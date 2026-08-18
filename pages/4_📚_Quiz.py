import time
import streamlit as st
from services.redis_service import redis_service

st.set_page_config(page_title="Take Quiz - Redis Quiz", page_icon="📚", layout="wide")

user = st.session_state.get("user")

# ADMIN & ROLE RESTRICTION
if not user:
    st.warning("⚠️ Access Restricted: Please sign in as a Student to take quizzes.")
    if st.button("🔑 Go to Login"):
        st.switch_page("Home.py")
elif user.get("role") == "admin":
    st.error("🚫 Admin Restriction: Admin users cannot take student quizzes or submit scores.")
    if st.button("⚙️ Return to Admin Dashboard", type="primary"):
        st.switch_page("pages/7_⚙_Admin_Dashboard.py")
else:
    # Sidebar Navigation
    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")
    if st.sidebar.button("👤 Student Dashboard", use_container_width=True):
        st.switch_page("pages/3_👤_Student_Dashboard.py")
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.user = None
        st.session_state.auth_role = None
        st.switch_page("Home.py")

    st.markdown("""
        <div style="border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; margin-bottom: 20px;">
            <h1 style="font-size: 2rem; color: #2dd4bf; margin: 0;">📚 Interactive Quiz Portal</h1>
            <p style="color: #94a3b8; font-size: 0.95rem;">Answer questions carefully. Scores are updated live into Redis memory!</p>
        </div>
    """, unsafe_allow_html=True)

    quizzes = st.session_state.get("quizzes", [])

    if not quizzes:
        st.info("No quizzes available currently.")
    else:
        # Default quiz selection
        active_id = st.session_state.get("active_quiz_id", quizzes[0]["id"])
        selected_quiz = next((q for q in quizzes if q["id"] == active_id), quizzes[0])

        st.selectbox(
            "Select Quiz Topic:",
            options=[q["id"] for q in quizzes],
            index=[q["id"] for q in quizzes].index(selected_quiz["id"]),
            format_func=lambda q_id: next(q["title"] for q in quizzes if q["id"] == q_id),
            key="quiz_selector"
        )

        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.85); padding: 18px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.3); margin-bottom: 25px;">
                <h3 style="color:#2dd4bf; margin:0;">{selected_quiz['title']}</h3>
                <p style="color:#cbd5e1; font-size:0.95rem; margin-top:4px;">{selected_quiz['description']}</p>
                <div style="font-size:0.85rem; color:#34d399;">
                    ⏱️ Duration: <b>{selected_quiz['duration_minutes']} Minutes</b> | 📝 Questions: <b>{len(selected_quiz.get('questions', []))}</b>
                </div>
            </div>
        """, unsafe_allow_html=True)

        questions = selected_quiz.get("questions", [])

        if not questions:
            st.info("No questions in this quiz category yet.")
        else:
            with st.form("quiz_submission_form"):
                user_answers = {}

                for idx, q in enumerate(questions, 1):
                    st.markdown(f"""
                        <div style="background: rgba(15,23,42,0.6); padding: 16px; border-radius: 10px; border-left: 4px solid #2dd4bf; margin-bottom: 16px;">
                            <span style="color:#2dd4bf; font-weight:bold;">Question {idx}:</span> <span style="color:#f8fafc; font-size:1.02rem;">{q['question']}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    user_answers[q["id"]] = st.radio(
                        f"Select your answer for Question {idx}:",
                        options=q["options"],
                        key=f"q_radio_{selected_quiz['id']}_{q['id']}",
                        label_visibility="collapsed"
                    )

                    st.markdown("<br>", unsafe_allow_html=True)

                submit_btn = st.form_submit_button("🚀 Submit Quiz & Calculate Score", type="primary", use_container_width=True)

                if submit_btn:
                    correct_count = 0
                    detailed_results = []

                    for q in questions:
                        selected_ans = user_answers.get(q["id"])
                        is_correct = (selected_ans == q["correct_answer"])
                        if is_correct:
                            correct_count += 1

                        detailed_results.append({
                            "question": q["question"],
                            "user_answer": selected_ans,
                            "correct_answer": q["correct_answer"],
                            "is_correct": is_correct
                        })

                    total_questions = len(questions)
                    score = float(correct_count)

                    # Save score in Redis Sorted Set (ZADD)
                    redis_service.save_score(selected_quiz["id"], user["username"], score)

                    # Record attempt in Redis List (LPUSH)
                    redis_service.record_attempt(user["username"], selected_quiz["title"], score, total_questions)

                    # Get updated rank from Redis Sorted Set (ZREVRANK)
                    user_rank = redis_service.get_user_rank(selected_quiz["id"], user["username"])

                    # Store results in session state for Result page
                    st.session_state.last_result = {
                        "quiz_title": selected_quiz["title"],
                        "score": correct_count,
                        "total": total_questions,
                        "correct": correct_count,
                        "wrong": total_questions - correct_count,
                        "percentage": int((correct_count / total_questions) * 100),
                        "rank": user_rank or 1,
                        "breakdown": detailed_results
                    }

                    # Redirect directly to Result Page
                    st.switch_page("pages/5_📊_Result.py")
