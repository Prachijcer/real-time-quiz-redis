import streamlit as st
import pandas as pd
from services.redis_service import redis_service

st.set_page_config(page_title="Student Dashboard - Redis Quiz", page_icon="👤", layout="wide")

user = st.session_state.get("user")

if not user or user.get("role") != "student":
    st.warning("⚠️ Access Restricted: Please log in as a Student.")
    if st.button("🔑 Go to Login"):
        st.switch_page("Home.py")
else:
    # Sidebar Logout & Navigation
    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.user = None
        st.session_state.auth_role = None
        st.switch_page("Home.py")

    # Header Welcome Banner
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(4, 47, 46, 0.9) 100%); padding: 24px; border-radius: 16px; border: 1px solid rgba(45, 212, 191, 0.3); margin-bottom: 25px;">
            <h1 style="color: #2dd4bf; margin: 0; font-size: 2.2rem;">Welcome, {user['name']}! 👋</h1>
            <p style="color: #cbd5e1; font-size: 1rem; margin-top: 6px;">Select an available quiz below, track your attempt history, and compete on the real-time leaderboard.</p>
        </div>
    """, unsafe_allow_html=True)

    username = user["username"]
    quizzes = st.session_state.get("quizzes", [])

    # Fetch Real Attempt History from Redis List
    user_attempts = redis_service.get_user_attempts(username)
    quizzes_attempted_count = len(set(a["quiz"] for a in user_attempts)) if user_attempts else 0
    total_attempts_count = len(user_attempts)

    # Compute Best & Average Score from Redis
    scores = []
    for a in user_attempts:
        try:
            # score format "8/10"
            parts = a["score"].split("/")
            scores.append(int(parts[0]))
        except Exception:
            pass

    best_score = max(scores) if scores else 0
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    # KPI Summary Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.8); padding: 16px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                <div style="font-size: 0.85rem; color: #94a3b8;">Available Quizzes</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #2dd4bf;">{len(quizzes)}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.8); padding: 16px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                <div style="font-size: 0.85rem; color: #94a3b8;">Quizzes Attempted</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #38bdf8;">{quizzes_attempted_count}</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.8); padding: 16px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                <div style="font-size: 0.85rem; color: #94a3b8;">Total Attempts</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #818cf8;">{total_attempts_count}</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.8); padding: 16px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                <div style="font-size: 0.85rem; color: #94a3b8;">Best Score</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #34d399;">{best_score}/10</div>
            </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.8); padding: 16px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                <div style="font-size: 0.85rem; color: #94a3b8;">Average Score</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #f43f5e;">{avg_score}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # AVAILABLE QUIZZES SECTION
    st.markdown("### 📚 Available Quizzes")
    if not quizzes:
        st.info("No quizzes available currently.")
    else:
        q_cols = st.columns(min(len(quizzes), 2))
        for idx, q in enumerate(quizzes):
            col_target = q_cols[idx % 2]
            with col_target:
                st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.85); padding: 22px; border-radius: 14px; border: 1px solid rgba(45, 212, 191, 0.3); margin-bottom: 20px;">
                        <h3 style="color: #2dd4bf; margin-top: 0; margin-bottom: 6px;">{q['title']}</h3>
                        <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 12px;">{q['description']}</p>
                        <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 16px;">
                            • <b>Questions:</b> {len(q.get('questions', []))} Questions<br>
                            • <b>Duration:</b> {q['duration_minutes']} Minutes<br>
                            • <b>Status:</b> <span style="color:#34d399; font-weight:bold;">Active</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"▶️ Start Quiz ({q['title']})", key=f"start_q_{q['id']}", type="primary", use_container_width=True):
                    st.session_state.active_quiz_id = q["id"]
                    st.switch_page("pages/4_📚_Quiz.py")

    st.markdown("<br>", unsafe_allow_html=True)

    # MY ATTEMPTS SECTION
    st.markdown("### 📜 My Attempts History")
    if not user_attempts:
        st.info("You haven't attempted any quizzes yet. Click 'Start Quiz' above!")
    else:
        df_attempts = pd.DataFrame(user_attempts)
        df_attempts.rename(columns={
            "quiz": "Quiz",
            "score": "Score",
            "percentage": "Percentage",
            "date": "Date / Time",
            "status": "Status"
        }, inplace=True)
        st.dataframe(df_attempts, use_container_width=True, hide_index=True)
