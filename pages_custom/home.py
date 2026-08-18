import streamlit as st
from utils.ui import render_page_header, render_stat_card
from services.analytics_service import analytics_service
from services.redis_service import redis_service

def render():
    render_page_header(
        "Real-Time Quiz Analytics & Leaderboard System",
        "High-performance college quiz platform powered by Redis Sorted Sets & Streamlit",
        "⚡"
    )

    # Hero Banner
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%);
                    padding: 30px; border-radius: 16px; border: 1px solid rgba(129, 140, 248, 0.3); margin-bottom: 25px;">
            <h2 style="color: #c084fc; margin-top: 0;">🚀 Sub-Millisecond Real-Time Rankings with Redis</h2>
            <p style="font-size: 1.1rem; color: #cbd5e1; line-height: 1.6;">
                Experience ultra-fast live score storage, automatic rank ordering using <b>Redis Sorted Sets</b> (<code>ZADD</code>, <code>ZREVRANGE</code>),
                session state tracking in <b>Redis Hashes</b>, and interactive student analytics.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Key Stat Cards
    kpis = analytics_service.get_kpi_summary()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card("Active Quizzes", kpis["total_quizzes"], "#6366f1")
    with c2:
        render_stat_card("Total Attempts", kpis["total_attempts"], "#818cf8")
    with c3:
        render_stat_card("Average Score", f"{kpis['avg_score']} pts", "#34d399")
    with c4:
        render_stat_card("Active Now (Redis)", kpis["active_participants"], "#f43f5e")

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick Navigation / Action Buttons
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("👨‍🎓 Student Portal")
        st.markdown("Take interactive multiple-choice quizzes with live countdown timers and track your global rank.")
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            if st.button("📝 Register Account", use_container_width=True):
                st.session_state.page = "Register"
                st.rerun()
        with c_sub2:
            if st.button("🔑 Student Login", use_container_width=True):
                st.session_state.page = "Login"
                st.rerun()

    with col_right:
        st.subheader("⚙️ Admin & Leaderboard")
        st.markdown("Access live leaderboard rankings or inspect real-time performance analytics.")
        c_adm1, c_adm2 = st.columns(2)
        with c_adm1:
            if st.button("🏆 Live Leaderboard", use_container_width=True):
                st.session_state.page = "Live Leaderboard"
                st.rerun()
        with c_adm2:
            if st.button("📊 Admin Analytics", use_container_width=True):
                st.session_state.page = "Analytics Dashboard"
                st.rerun()

    st.markdown("---")

    # Redis Data Structures Technical Diagram / Summary
    st.subheader("🔍 Core Redis Architecture")

    r_col1, r_col2, r_col3, r_col4 = st.columns(4)

    with r_col1:
        st.markdown("""
            <div class="quiz-card">
                <h4 style="color:#818cf8;">🏆 Sorted Sets</h4>
                <p><code>leaderboard:&lt;quiz_id&gt;</code></p>
                <span class="badge badge-info">ZADD / ZREVRANGE</span>
                <p style="font-size:0.85rem; color:#94a3b8; margin-top:8px;">
                    Ranks students instantly by score in O(log N) time.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with r_col2:
        st.markdown("""
            <div class="quiz-card">
                <h4 style="color:#c084fc;">👤 Hashes</h4>
                <p><code>session:&lt;username&gt;</code></p>
                <span class="badge badge-purple">HSET / HGETALL</span>
                <p style="font-size:0.85rem; color:#94a3b8; margin-top:8px;">
                    Stores active student session details & start timestamps.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with r_col3:
        st.markdown("""
            <div class="quiz-card">
                <h4 style="color:#34d399;">🟢 Sets</h4>
                <p><code>active_participants</code></p>
                <span class="badge badge-success">SADD / SCARD</span>
                <p style="font-size:0.85rem; color:#94a3b8; margin-top:8px;">
                    Tracks unique students currently attempting quizzes.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with r_col4:
        st.markdown("""
            <div class="quiz-card">
                <h4 style="color:#fbbf24;">📡 Pub / Sub</h4>
                <p><code>leaderboard_updates</code></p>
                <span class="badge badge-warning">PUBLISH</span>
                <p style="font-size:0.85rem; color:#94a3b8; margin-top:8px;">
                    Broadcasts live events when scores are submitted.
                </p>
            </div>
        """, unsafe_allow_html=True)
