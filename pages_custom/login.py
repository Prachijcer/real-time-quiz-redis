import streamlit as st
from utils.ui import render_page_header
from services.auth_service import auth_service
from services.redis_service import redis_service

def render():
    render_page_header("Portal Authentication", "Login as a Student to take quizzes or as an Admin to manage quizzes", "🔑")

    tab_student, tab_admin = st.tabs(["👨‍🎓 Student Login", "⚙️ Admin Login"])

    with tab_student:
        col1, _ = st.columns([2, 1])
        with col1:
            st.markdown("""
                <div class="quiz-card">
                    <h3 style="color:#818cf8; margin-top:0;">Student Sign In</h3>
                    <p style="color:#94a3b8; font-size:0.9rem;">Default testing account: <b>prachi</b> / <b>password123</b></p>
                </div>
            """, unsafe_allow_html=True)

            with st.form("student_login_form"):
                username = st.text_input("Username", value="prachi")
                password = st.text_input("Password", type="password", value="password123")
                submit = st.form_submit_button("Sign In as Student", use_container_width=True)

                if submit:
                    res = auth_service.authenticate_user(username, password, expected_role="student")
                    if res["success"]:
                        st.session_state.user = res["user"]
                        st.session_state.is_logged_in = True
                        st.session_state.role = "student"

                        # Track active user login in Redis
                        if redis_service.client:
                            redis_service.client.hset(
                                f"active_login:{username}",
                                mapping={"logged_in_at": str(st.session_state.user)}
                            )

                        st.success(res["message"])
                        st.session_state.page = "Student Dashboard"
                        st.rerun()
                    else:
                        st.error(res["message"])

    with tab_admin:
        col2, _ = st.columns([2, 1])
        with col2:
            st.markdown("""
                <div class="quiz-card">
                    <h3 style="color:#c084fc; margin-top:0;">Admin Sign In</h3>
                    <p style="color:#94a3b8; font-size:0.9rem;">Admin credentials: <b>admin</b> / <b>admin123</b></p>
                </div>
            """, unsafe_allow_html=True)

            with st.form("admin_login_form"):
                admin_user = st.text_input("Admin Username", value="admin")
                admin_pwd = st.text_input("Admin Password", type="password", value="admin123")
                admin_submit = st.form_submit_button("Sign In as Admin", use_container_width=True)

                if admin_submit:
                    res = auth_service.authenticate_user(admin_user, admin_pwd, expected_role="admin")
                    if res["success"]:
                        st.session_state.user = res["user"]
                        st.session_state.is_logged_in = True
                        st.session_state.role = "admin"

                        st.success("Admin login successful!")
                        st.session_state.page = "Analytics Dashboard"
                        st.rerun()
                    else:
                        st.error(res["message"])
