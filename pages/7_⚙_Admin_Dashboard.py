import streamlit as st
import pandas as pd
import plotly.express as px
from services.redis_service import redis_service

st.set_page_config(page_title="Admin Dashboard - Redis Quiz", page_icon="⚙️", layout="wide")

user = st.session_state.get("user")

if not user or user.get("role") != "admin":
    st.warning("⚠️ Access Restricted: Please log in as Admin on the homepage.")
    if st.button("🔑 Go to Homepage"):
        st.switch_page("Home.py")
else:
    # Sidebar Admin Navigation
    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.user = None
        st.session_state.auth_role = None
        st.switch_page("Home.py")

    # Admin Header Banner
    st.markdown("""
        <div style="border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; margin-bottom: 20px;">
            <h1 style="font-size: 2rem; color: #2dd4bf; margin: 0;">⚙️ Admin Dashboard & Control Center</h1>
            <p style="color: #94a3b8; font-size: 0.95rem;">Manage quizzes, view participants, inspect live leaderboards, analytics & real Redis memory state</p>
        </div>
    """, unsafe_allow_html=True)

    # 5 Admin Navigation Tabs
    tab_quizzes, tab_participants, tab_leaderboard, tab_analytics, tab_redis = st.tabs([
        "🛠️ Manage Quizzes",
        "👥 Participants",
        "🏆 Live Leaderboard",
        "📈 Analytics",
        "⚡ Redis Status & Data"
    ])

    # =========================================================================
    # SECTION 1: MANAGE QUIZZES
    # =========================================================================
    with tab_quizzes:
        quizzes = st.session_state.get("quizzes", [])

        st.subheader("📚 Available Quizzes Overview")
        if not quizzes:
            st.info("No quizzes available yet.")
        else:
            for q in quizzes:
                q_count = len(q.get("questions", []))
                st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.85); padding: 18px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.25); margin-bottom: 15px;">
                        <h3 style="color:#2dd4bf; margin:0;">{q['title']}</h3>
                        <p style="color:#cbd5e1; font-size:0.95rem; margin-top:4px;">{q['description']}</p>
                        <p style="color:#94a3b8; font-size:0.85rem;">
                            <b>Questions:</b> {q_count} &nbsp;|&nbsp; 
                            <b>Duration:</b> {q['duration_minutes']} Mins &nbsp;|&nbsp; 
                            <b>Status:</b> <span style="color:#34d399; font-weight:bold;">Active</span>
                        </p>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        col_q1, col_q2 = st.columns(2)

        # Create New Quiz Form
        with col_q1:
            st.subheader("➕ Create a New Quiz")
            with st.form("create_quiz_form"):
                new_title = st.text_input("Quiz Title", placeholder="e.g. Python Advanced")
                new_desc = st.text_area("Description", placeholder="Describe the topics covered...")
                new_duration = st.number_input("Duration (Minutes)", min_value=1, value=5)
                create_submit = st.form_submit_button("Create Quiz Category", type="primary", use_container_width=True)

                if create_submit:
                    if not new_title or not new_desc:
                        st.error("Quiz title and description are required.")
                    else:
                        new_quiz_id = f"quiz_{new_title.lower().replace(' ', '_')}"
                        new_q_obj = {
                            "id": new_quiz_id,
                            "title": new_title.strip(),
                            "description": new_desc.strip(),
                            "duration_minutes": new_duration,
                            "questions": []
                        }
                        if "quizzes" not in st.session_state:
                            st.session_state.quizzes = []
                        st.session_state.quizzes.append(new_q_obj)
                        st.success(f"Quiz '{new_title}' created successfully!")
                        st.rerun()

        # Delete Quiz Form
        with col_q2:
            st.subheader("🗑️ Delete a Quiz Category")
            if quizzes:
                with st.form("delete_quiz_form"):
                    del_quiz_id = st.selectbox(
                        "Select Quiz to Delete:",
                        options=[q["id"] for q in quizzes],
                        format_func=lambda q_id: next(q["title"] for q in quizzes if q["id"] == q_id)
                    )
                    del_submit = st.form_submit_button("Delete Quiz Category", use_container_width=True)

                    if del_submit:
                        st.session_state.quizzes = [q for q in quizzes if q["id"] != del_quiz_id]
                        redis_service.delete_quiz_leaderboard(del_quiz_id)
                        st.success("Quiz category and its Redis leaderboard deleted successfully!")
                        st.rerun()

        st.markdown("---")
        # Manage Questions inside Selected Quiz
        st.subheader("❓ Manage Questions Bank")
        if quizzes:
            target_quiz_id = st.selectbox(
                "Select Quiz Category to Manage Questions:",
                options=[q["id"] for q in quizzes],
                format_func=lambda q_id: next(q["title"] for q in quizzes if q["id"] == q_id),
                key="manage_q_select"
            )

            selected_quiz = next(q for q in quizzes if q["id"] == target_quiz_id)
            questions = selected_quiz.get("questions", [])

            st.markdown(f"#### Questions List for '{selected_quiz['title']}' ({len(questions)} Total)")
            if not questions:
                st.info("No questions in this quiz yet.")
            else:
                for idx, q in enumerate(questions, 1):
                    with st.expander(f"Question {idx}: {q['question']}"):
                        st.write(f"**Options:** {', '.join(q['options'])}")
                        st.write(f"**Correct Answer:** ✅ `{q['correct_answer']}`")

                        col_edit, col_del = st.columns(2)
                        with col_del:
                            if st.button(f"🗑️ Delete Question {idx}", key=f"del_q_{q['id']}"):
                                selected_quiz["questions"] = [item for item in selected_quiz["questions"] if item["id"] != q["id"]]
                                st.success("Question deleted!")
                                st.rerun()

    # =========================================================================
    # SECTION 2: PARTICIPANTS
    # =========================================================================
    with tab_participants:
        st.subheader("👥 Student Participants & Attempt History")
        raw_leaderboard = redis_service.get_leaderboard("overall")

        if not raw_leaderboard:
            st.info("No student attempts recorded yet.")
        else:
            participants_data = []
            for username, overall_score in raw_leaderboard:
                user_info = redis_service.get_user(username)
                name = user_info.get("name", username.capitalize())
                
                py_score = redis_service.get_user_score("quiz_python_basics", username)
                ds_score = redis_service.get_user_score("quiz_data_structures", username)

                if py_score is not None:
                    participants_data.append({
                        "Student Name": f"{name} (@{username})",
                        "Quiz": "Python Basics",
                        "Score": f"{int(py_score)}/10",
                        "Status": "Completed"
                    })
                if ds_score is not None:
                    participants_data.append({
                        "Student Name": f"{name} (@{username})",
                        "Quiz": "Data Structures",
                        "Score": f"{int(ds_score)}/10",
                        "Status": "Completed"
                    })

            if participants_data:
                df_part = pd.DataFrame(participants_data)
                st.dataframe(df_part, use_container_width=True, hide_index=True)
            else:
                st.info("No completed quiz attempts found.")

    # =========================================================================
    # SECTION 3: LIVE LEADERBOARD (REDIS SORTED SET)
    # =========================================================================
    with tab_leaderboard:
        st.subheader("🏆 Live Leaderboard (Sourced from Redis Sorted Sets)")
        quizzes = st.session_state.get("quizzes", [])
        quiz_options = {"overall": "🏆 Overall Leaderboard"}
        for q in quizzes:
            quiz_options[q["id"]] = f"📘 {q['title']}"

        selected_cat = st.selectbox(
            "Select Leaderboard Category:",
            options=list(quiz_options.keys()),
            format_func=lambda x: quiz_options[x],
            key="admin_lb_cat"
        )

        raw_lb = redis_service.get_leaderboard(selected_cat)
        if not raw_lb:
            st.info("No rankings recorded in Redis for this category yet.")
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

    # =========================================================================
    # SECTION 4: ANALYTICS
    # =========================================================================
    with tab_analytics:
        st.subheader("📈 Quiz Analytics & Key Performance Indicators")
        raw_leaderboard = redis_service.get_leaderboard("overall")
        total_attempts = len(raw_leaderboard)
        unique_participants = len(set(u for u, _ in raw_leaderboard)) if raw_leaderboard else 0
        scores = [s for _, s in raw_leaderboard] if raw_leaderboard else [0]
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        highest_score = max(scores) if scores else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.8); padding: 16px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                    <div style="font-size: 0.85rem; color: #94a3b8;">Total Participants</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #2dd4bf;">{unique_participants}</div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.8); padding: 16px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                    <div style="font-size: 0.85rem; color: #94a3b8;">Total Quiz Attempts</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #38bdf8;">{total_attempts}</div>
                </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.8); padding: 16px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                    <div style="font-size: 0.85rem; color: #94a3b8;">Average Score</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #818cf8;">{avg_score}</div>
                </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.8); padding: 16px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                    <div style="font-size: 0.85rem; color: #94a3b8;">Highest Score</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #34d399;">{highest_score:.0f} pts</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("1. Score Distribution")
            if raw_leaderboard:
                df_scores = pd.DataFrame([{"Student": u, "Score": s} for u, s in raw_leaderboard])
                fig1 = px.histogram(df_scores, x="Score", title="Score Distribution", color_discrete_sequence=["#14b8a6"], template="plotly_dark")
                fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig1, use_container_width=True)

        with col_chart2:
            st.subheader("2. Average Score by Quiz Category")
            quizzes = st.session_state.get("quizzes", [])
            quiz_data = []
            for q in quizzes:
                q_lb = redis_service.get_leaderboard(q["id"])
                q_scores = [s for _, s in q_lb]
                q_avg = round(sum(q_scores) / len(q_scores), 2) if q_scores else 0.0
                quiz_data.append({"Quiz Title": q["title"], "Average Score": q_avg})

            fig2 = px.bar(pd.DataFrame(quiz_data), x="Quiz Title", y="Average Score", color="Quiz Title", title="Average Marks per Quiz", template="plotly_dark")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

    # =========================================================================
    # SECTION 5: REDIS STATUS & LIVE DATA INSPECTOR (KEY VIVA DEMO FEATURE)
    # =========================================================================
    with tab_redis:
        st.subheader("⚡ Redis Status & Memory Inspector")
        status = redis_service.get_status()

        if status["connected"]:
            st.success(f"🟢 **Redis Status**: Connected\n\n**Server Location**: `{status['host']}:{status['port']}`")
        else:
            st.error(f"🔴 **Redis Status**: Disconnected\n\n**Server Location**: `{status['host']}:{status['port']}`")

        st.markdown("---")
        st.subheader("🔍 Real-Time Redis Memory Explorer")
        st.caption("Demonstrate to college faculty that scores, leaderboards, and user sessions are stored directly in Redis memory.")

        all_keys = redis_service.get_all_keys()
        if not all_keys:
            st.info("No keys currently found in Redis memory. Take a quiz to generate live keys!")
        else:
            st.write(f"**Total Redis Keys Count**: `{len(all_keys)}`")
            selected_key = st.selectbox("Select Redis Key to Inspect Raw Memory:", options=all_keys)

            if selected_key:
                info = redis_service.get_key_info(selected_key)
                st.markdown(f"**Key Name**: `{info['key']}` | **Data Type**: `{info['type'].upper()}`")
                
                st.markdown("##### Raw Stored Content:")
                st.json({
                    "redis_key": info["key"],
                    "redis_data_type": info["type"],
                    "memory_value": info["value"]
                })
