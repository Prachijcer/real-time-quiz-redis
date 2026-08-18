import streamlit as st
from services.redis_service import redis_service

st.set_page_config(page_title="Login - Redis Quiz", page_icon="🔑", layout="wide")

st.markdown("""
    <div style="border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; margin-bottom: 20px;">
        <h1 style="font-size: 2rem; color: #2dd4bf; margin: 0;">🔑 Authentication Portal</h1>
        <p style="color: #94a3b8; font-size: 0.95rem;">Log in as Student or Admin</p>
    </div>
""", unsafe_allow_html=True)

tab_student, tab_admin = st.tabs(["👨‍🎓 Student Login", "⚙️ Admin Login"])

# 1. Student Login
with tab_student:
    col1, _ = st.columns([2, 1])
    with col1:
        st.markdown("""
            <div style="background: rgba(15,23,42,0.8); padding: 18px; border-radius: 12px; border: 1px solid rgba(45,212,191,0.2);">
                <h3 style="color:#2dd4bf; margin-top:0;">Student Sign In</h3>
                <p style="color:#94a3b8; font-size:0.85rem;">Demo account: <b>prachi</b> / <b>password123</b></p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("student_login_form"):
            username = st.text_input("Username", value="prachi")
            password = st.text_input("Password", type="password", value="password123")
            submit = st.form_submit_button("Sign In as Student", use_container_width=True, type="primary")

            if submit:
                user_clean = username.strip().lower()
                user_info = redis_service.get_user(user_clean)
                name = user_info.get("name", user_clean.capitalize())

                st.session_state.user = {
                    "username": user_clean,
                    "name": name,
                    "role": "student"
                }
                # AUTOMATIC INSTANT REDIRECT TO STUDENT DASHBOARD
                st.switch_page("pages/3_👤_Student_Dashboard.py")

# 2. Admin Login
with tab_admin:
    col2, _ = st.columns([2, 1])
    with col2:
        st.markdown("""
            <div style="background: rgba(15,23,42,0.8); padding: 18px; border-radius: 12px; border: 1px solid rgba(45,212,191,0.2);">
                <h3 style="color:#f43f5e; margin-top:0;">Admin Sign In</h3>
                <p style="color:#94a3b8; font-size:0.85rem;">Admin credentials: <b>admin</b> / <b>admin123</b></p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("admin_login_form"):
            adm_user = st.text_input("Admin Username", value="admin")
            adm_pass = st.text_input("Admin Password", type="password", value="admin123")
            adm_submit = st.form_submit_button("Sign In as Admin", use_container_width=True, type="primary")

            if adm_submit:
                if adm_user.strip().lower() == "admin" and adm_pass == "admin123":
                    st.session_state.user = {
                        "username": "admin",
                        "name": "System Administrator",
                        "role": "admin"
                    }
                    # AUTOMATIC INSTANT REDIRECT TO ADMIN DASHBOARD
                    st.switch_page("pages/7_⚙_Admin_Dashboard.py")
                else:
                    st.error("Invalid Admin credentials.")
