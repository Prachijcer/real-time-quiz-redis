import streamlit as st
from utils.ui import render_page_header
from services.auth_service import auth_service

def render():
    render_page_header("Student Registration", "Create your account to participate in live real-time quizzes", "📝")

    col_center, _ = st.columns([2, 1])

    with col_center:
        st.markdown("""
            <div class="quiz-card">
                <h3 style="color:#818cf8; margin-top:0;">New Student Account</h3>
                <p style="color:#94a3b8; font-size:0.9rem;">Fill in your details below. Username must be unique.</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("register_form", clear_on_submit=False):
            name = st.text_input("Full Name", placeholder="e.g. Prachi Sharma")
            username = st.text_input("Username", placeholder="e.g. prachi")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            submitted = st.form_submit_button("Register Account", use_container_width=True)

            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match. Please re-enter.")
                else:
                    res = auth_service.register_user(username, name, password)
                    if res["success"]:
                        st.success(res["message"])
                        st.info("You can now login with your credentials.")
                        if st.button("Go to Login Page"):
                            st.session_state.page = "Login"
                            st.rerun()
                    else:
                        st.error(res["message"])

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Already have an account? Log In"):
            st.session_state.page = "Login"
            st.rerun()
