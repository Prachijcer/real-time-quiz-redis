import streamlit as st
from utils.ui import render_page_header, render_stat_card
from services.analytics_service import analytics_service
from services.quiz_service import quiz_service

def render():
    role = st.session_state.get("role")
    if role != "admin":
        st.warning("⚠️ Access Restricted: Analytics Dashboard is for Admins only.")
        if st.button("Log in as Admin"):
            st.session_state.page = "Login"
            st.rerun()
        return

    render_page_header("Admin Analytics Dashboard", "Real-time visualization of student performance & quiz metrics", "📊")

    # KPI Summary Cards
    kpis = analytics_service.get_kpi_summary()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_stat_card("Participants", kpis["total_participants"], "#6366f1")
    with c2:
        render_stat_card("Total Attempts", kpis["total_attempts"], "#818cf8")
    with c3:
        render_stat_card("Avg Score", f"{kpis['avg_score']}", "#34d399")
    with c4:
        render_stat_card("Highest Score", f"{kpis['highest_score']}", "#c084fc")
    with c5:
        render_stat_card("Lowest Score", f"{kpis['lowest_score']}", "#f87171")
    with c6:
        render_stat_card("Active Now", kpis["active_participants"], "#f43f5e")

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter Bar
    quizzes = quiz_service.get_all_quizzes()
    quiz_options = {"all": "All Quizzes"}
    for q in quizzes:
        quiz_options[q["id"]] = q["title"]

    selected_quiz = st.selectbox(
        "Filter Analytics by Quiz Category:",
        options=list(quiz_options.keys()),
        format_func=lambda x: quiz_options[x]
    )

    st.markdown("---")

    # Row 1 Charts: Score Distribution & Leaderboard Top 5
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig_dist = analytics_service.get_score_distribution_chart(selected_quiz)
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_chart2:
        fig_top = analytics_service.get_top_leaderboard_chart(selected_quiz)
        st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2 Charts: Question Performance & Quiz Average
    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        q_target = selected_quiz if selected_quiz != "all" else (quizzes[0]["id"] if quizzes else "all")
        fig_q = analytics_service.get_question_performance_chart(q_target)
        st.plotly_chart(fig_q, use_container_width=True)

    with col_chart4:
        fig_quiz_avg = analytics_service.get_quiz_performance_chart()
        st.plotly_chart(fig_quiz_avg, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 3 Chart: Participation Breakdown
    fig_part = analytics_service.get_participation_chart()
    st.plotly_chart(fig_part, use_container_width=True)
