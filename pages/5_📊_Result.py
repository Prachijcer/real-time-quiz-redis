import streamlit as st

st.set_page_config(page_title="Quiz Result - Redis Quiz", page_icon="📊", layout="wide")

user = st.session_state.get("user")
result = st.session_state.get("last_result")

if not user or not result:
    st.warning("⚠️ No quiz result found. Please take a quiz first!")
    if st.button("⬅️ Go to Student Dashboard"):
        st.switch_page("pages/3_👤_Student_Dashboard.py")
else:
    # Sidebar Navigation
    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")
    if st.sidebar.button("👤 Student Dashboard", use_container_width=True):
        st.switch_page("pages/3_👤_Student_Dashboard.py")
    if st.sidebar.button("🏆 Live Leaderboard", use_container_width=True):
        st.switch_page("pages/6_🏆_Live_Leaderboard.py")
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.user = None
        st.session_state.auth_role = None
        st.switch_page("Home.py")

    # Result Header
    st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #2dd4bf; margin: 0; font-size: 2.2rem;">🎉 Quiz Result Card</h1>
            <p style="color: #cbd5e1; font-size: 1.1rem; margin-top: 6px;">Quiz: <b style="color:#34d399;">{result['quiz_title']}</b></p>
        </div>
    """, unsafe_allow_html=True)

    # Score Card Banner
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(4, 47, 46, 0.9) 100%); padding: 30px; border-radius: 16px; border: 1px solid rgba(45, 212, 191, 0.35); text-align: center; max-width: 750px; margin: 0 auto 30px auto; box-shadow: 0 10px 40px rgba(0,0,0,0.4);">
            <div style="font-size: 1.1rem; color: #94a3b8;">YOUR SCORE</div>
            <div style="font-size: 3.5rem; font-weight: 800; color: #2dd4bf; margin: 6px 0;">{result['score']} / {result['total']}</div>
            <div style="font-size: 1.2rem; color: #34d399; font-weight: 600;">Percentage: {result['percentage']}%</div>
        </div>
    """, unsafe_allow_html=True)

    # Result Metric Breakdown Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.8); padding: 18px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                <div style="font-size: 0.85rem; color: #94a3b8;">Score</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #2dd4bf;">{result['score']}/{result['total']}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.8); padding: 18px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                <div style="font-size: 0.85rem; color: #94a3b8;">Correct Answers</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #34d399;">{result['correct']}</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.8); padding: 18px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                <div style="font-size: 0.85rem; color: #94a3b8;">Wrong Answers</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #f43f5e;">{result['wrong']}</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.8); padding: 18px; border-radius: 12px; border: 1px solid rgba(45, 212, 191, 0.2); text-align: center;">
                <div style="font-size: 0.85rem; color: #94a3b8;">Live Redis Rank</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #fbbf24;">#{result['rank']}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # BACK TO DASHBOARD & ACTION BUTTONS
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("⬅️ Back to Student Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/3_👤_Student_Dashboard.py")
    with col_b2:
        if st.button("🏆 View Live Leaderboard", use_container_width=True):
            st.switch_page("pages/6_🏆_Live_Leaderboard.py")

    st.markdown("---")

    # Detailed Question Breakdown
    st.subheader("📋 Detailed Question Review")
    for idx, item in enumerate(result["breakdown"], 1):
        icon = "✅" if item["is_correct"] else "❌"
        color = "#34d399" if item["is_correct"] else "#f43f5e"

        with st.expander(f"{icon} Question {idx}: {item['question']}"):
            st.markdown(f"**Your Answer:** <span style='color:{color}; font-weight:bold;'>{item['user_answer']}</span>", unsafe_allow_html=True)
            if not item["is_correct"]:
                st.markdown(f"**Correct Answer:** <span style='color:#34d399; font-weight:bold;'>{item['correct_answer']}</span>", unsafe_allow_html=True)
