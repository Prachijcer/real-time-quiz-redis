import streamlit as st
import pandas as pd
from utils.ui import render_page_header
from services.quiz_service import quiz_service

def render():
    role = st.session_state.get("role")
    if role != "admin":
        st.warning("⚠️ Access Restricted: Admin permissions required.")
        if st.button("Log in as Admin"):
            st.session_state.page = "Login"
            st.rerun()
        return

    render_page_header("Admin Quiz Management", "Create & manage quizzes, edit question banks, and set parameters", "⚙️")

    tab_manage, tab_create_quiz, tab_add_q = st.tabs(["📚 Quiz Overview & Questions", "➕ Create New Quiz", "❓ Add New Question"])

    # Tab 1: Manage Questions
    with tab_manage:
        quizzes = quiz_service.get_all_quizzes()
        if not quizzes:
            st.info("No quizzes created yet.")
        else:
            selected_quiz_id = st.selectbox(
                "Select Quiz to Manage:",
                options=[q["id"] for q in quizzes],
                format_func=lambda q_id: next(q["title"] for q in quizzes if q["id"] == q_id)
            )

            quiz = quiz_service.get_quiz_by_id(selected_quiz_id)
            questions = quiz_service.get_questions_for_quiz(selected_quiz_id)

            st.markdown(f"""
                <div class="quiz-card">
                    <h4 style="color:#818cf8; margin-top:0;">{quiz['title']}</h4>
                    <p style="color:#cbd5e1;">{quiz['description']}</p>
                    <p style="font-size:0.85rem; color:#94a3b8;">Duration: <b>{quiz['duration_minutes']} min</b> | Total Questions: <b>{len(questions)}</b></p>
                </div>
            """, unsafe_allow_html=True)

            st.subheader("Question List")
            if not questions:
                st.info("No questions added to this quiz yet. Use the 'Add New Question' tab to add questions.")
            else:
                for idx, q in enumerate(questions, 1):
                    with st.expander(f"Question {idx}: {q['question']}"):
                        st.write(f"**Options:** {', '.join(q['options'])}")
                        st.write(f"**Correct Answer:** ✅ `{q['correct_answer']}`")

                        col_edit, col_del = st.columns(2)
                        with col_del:
                            if st.button(f"🗑️ Delete Question {idx}", key=f"del_{q['id']}"):
                                if quiz_service.delete_question(q["id"]):
                                    st.success("Question deleted!")
                                    st.rerun()

    # Tab 2: Create New Quiz
    with tab_create_quiz:
        st.subheader("➕ Create a New Quiz Category")
        with st.form("create_quiz_form"):
            title = st.text_input("Quiz Title", placeholder="e.g. Advanced Python & AsyncIO")
            description = st.text_area("Description", placeholder="Describe the topic and learning objectives...")
            duration = st.number_input("Duration (Minutes)", min_value=1, max_value=120, value=5)

            submit_quiz = st.form_submit_button("Create Quiz", type="primary", use_container_width=True)

            if submit_quiz:
                if not title or not description:
                    st.error("Title and description are required.")
                else:
                    new_q = quiz_service.create_quiz(title, description, duration)
                    st.success(f"Quiz '{new_q['title']}' created successfully!")
                    st.rerun()

    # Tab 3: Add New Question
    with tab_add_q:
        st.subheader("❓ Add Question to Quiz")
        quizzes = quiz_service.get_all_quizzes()
        if not quizzes:
            st.warning("Please create a quiz category first before adding questions.")
        else:
            with st.form("add_question_form"):
                target_quiz_id = st.selectbox(
                    "Target Quiz Category:",
                    options=[q["id"] for q in quizzes],
                    format_func=lambda q_id: next(q["title"] for q in quizzes if q["id"] == q_id)
                )

                q_text = st.text_area("Question Text", placeholder="e.g. Which keyword is used to handle exceptions in Python?")
                opt_a = st.text_input("Option A", placeholder="try")
                opt_b = st.text_input("Option B", placeholder="catch")
                opt_c = st.text_input("Option C", placeholder="except")
                opt_d = st.text_input("Option D", placeholder="finally")

                correct_ans = st.selectbox("Select Correct Answer:", options=[opt_a, opt_b, opt_c, opt_d])

                submit_q = st.form_submit_button("Add Question to Quiz", type="primary", use_container_width=True)

                if submit_q:
                    options = [opt_a.strip(), opt_b.strip(), opt_c.strip(), opt_d.strip()]
                    if not q_text or any(not o for o in options):
                        st.error("All options and question text must be filled.")
                    elif not correct_ans:
                        st.error("Please select the correct answer.")
                    else:
                        quiz_service.add_question(target_quiz_id, q_text.strip(), options, correct_ans)
                        st.success("Question added successfully!")
                        st.rerun()
