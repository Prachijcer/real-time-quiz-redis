import streamlit as st
from services.redis_service import redis_service

st.set_page_config(page_title="Register - Redis Quiz", page_icon="📝", layout="wide")

st.markdown("""
    <div style="border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; margin-bottom: 20px;">
        <h1 style="font-size: 2rem; color: #2dd4bf; margin: 0;">📝 Student Registration</h1>
        <p style="color: #94a3b8; font-size: 0.95rem;">Create a new student account to participate in live quizzes</p>
    </div>
""", unsafe_allow_html=True)

col_center, _ = st.columns([2, 1])

with col_center:
    st.markdown("""
        <div style="background: rgba(15,23,42,0.8); padding: 20px; border-radius: 12px; border: 1px solid rgba(45,212,191,0.2);">
            <h3 style="color:#34d399; margin-top:0;">New Account Details</h3>
        </div>
    """, unsafe_allow_html=True)

    with st.form("registration_form"):
        name = st.text_input("Full Name", placeholder="e.g. Prachi Sharma")
        username = st.text_input("Username", placeholder="e.g. prachi")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Register Account", use_container_width=True, type="primary")

        if submitted:
            if not name or not username or not password:
                st.error("All fields are required.")
            else:
                user_clean = username.strip().lower()
                # Check if username already exists in Redis
                existing_user = redis_service.get_user(user_clean)
                if existing_user:
                    st.error(f"Username '{user_clean}' is already registered.")
                else:
                    # Save user profile in Redis Hash (HSET user:<username>)
                    redis_service.save_user(user_clean, name.strip(), "student")
                    st.success(f"Account for '{name}' created successfully! You can now log in.")
