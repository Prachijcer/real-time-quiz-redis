import json
import streamlit as st
from pathlib import Path
from services.redis_service import redis_service

# Streamlit Page Configuration
st.set_page_config(
    page_title="Home - Real-Time Quiz Analytics & Leaderboard System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Glassmorphic Styling
def inject_premium_styles():
    st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3.5rem;
            max-width: 950px;
        }

        .stApp {
            background: radial-gradient(circle at 50% 10%, #0f172a 0%, #042f2e 60%, #020617 100%);
            color: #f8fafc;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }

        .hero-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, #2dd4bf 0%, #38bdf8 50%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 10px;
            line-height: 1.25;
            letter-spacing: -0.02em;
        }

        .hero-subtitle {
            font-size: 1.15rem;
            color: #34d399;
            text-align: center;
            font-weight: 500;
            margin-bottom: 14px;
        }

        .hero-intro {
            font-size: 1rem;
            color: #cbd5e1;
            text-align: center;
            line-height: 1.65;
            margin-bottom: 32px;
            max-width: 780px;
            margin-left: auto;
            margin-right: auto;
        }

        .section-heading {
            font-size: 1.35rem;
            font-weight: 700;
            color: #f8fafc;
            text-align: center;
            margin-bottom: 18px;
            letter-spacing: 0.02em;
        }

        .role-card {
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(45, 212, 191, 0.3);
            border-radius: 16px;
            padding: 24px 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin-bottom: 10px;
        }

        .role-card:hover {
            border-color: #2dd4bf;
            box-shadow: 0 15px 35px rgba(20, 184, 166, 0.25);
            transform: translateY(-4px);
        }

        .guidelines-card {
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(45, 212, 191, 0.35);
            border-radius: 16px;
            padding: 24px 30px;
            margin: 40px auto 20px auto;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        }

        .guidelines-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #2dd4bf;
            text-align: center;
            margin-top: 0;
            margin-bottom: 16px;
            border-bottom: 1px solid rgba(45, 212, 191, 0.2);
            padding-bottom: 10px;
        }

        .guidelines-list {
            list-style: none;
            color: #e2e8f0;
            font-size: 0.98rem;
            line-height: 1.9;
            margin: 0;
            padding-left: 0;
        }

        .guidelines-list li {
            position: relative;
            padding-left: 28px;
            margin-bottom: 6px;
        }

        .guidelines-list li::before {
            content: "✔";
            position: absolute;
            left: 0;
            color: #34d399;
            font-weight: bold;
        }

        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            font-size: 1.05rem;
            padding: 12px 24px;
        }

        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%);
            border: none;
            box-shadow: 0 4px 15px rgba(20, 184, 166, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

inject_premium_styles()

# Seed Data on Startup
def seed_data():
    data_path = Path(__file__).resolve().parent / "data" / "quizzes.json"
    if data_path.exists():
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                st.session_state.quizzes = json.load(f)
        except Exception:
            pass

    sample_users = [
        {"username": "prachi", "name": "Prachi Sharma", "role": "student"},
        {"username": "shivam", "name": "Shivam Kumar", "role": "student"},
        {"username": "ananya", "name": "Ananya Verma", "role": "student"},
        {"username": "admin", "name": "System Admin", "role": "admin"}
    ]

    for u in sample_users:
        redis_service.save_user(u["username"], u["name"], u["role"])

    redis_service.save_score("quiz_python_basics", "prachi", 9)
    redis_service.save_score("quiz_python_basics", "shivam", 8)
    redis_service.save_score("quiz_python_basics", "ananya", 10)

    # Seed sample attempts into Redis List
    redis_service.record_attempt("prachi", "Python Basics", 9, 10)
    redis_service.record_attempt("shivam", "Python Basics", 8, 10)
    redis_service.record_attempt("ananya", "Python Basics", 10, 10)

if "seeded" not in st.session_state:
    seed_data()
    st.session_state.seeded = True

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #2dd4bf; margin: 0;">⚡ RedisQuiz AI</h2>
        <p style="color: #94a3b8; font-size: 0.8rem;">Real-Time Quiz & Leaderboard</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

user = st.session_state.get("user")

if user:
    st.sidebar.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.85); padding: 12px; border-radius: 10px; border: 1px solid rgba(45, 212, 191, 0.3); margin-bottom: 10px;">
            <div style="font-size:0.8rem; color:#94a3b8;">Logged in as:</div>
            <div style="font-weight:700; color:#34d399; font-size:1.05rem;">{user['name']}</div>
            <div style="font-size:0.8rem; color:#94a3b8;">@{user['username']} ({user['role'].capitalize()})</div>
        </div>
    """, unsafe_allow_html=True)

    if user["role"] == "admin":
        if st.sidebar.button("⚙️ Open Admin Dashboard", use_container_width=True):
            st.switch_page("pages/7_⚙_Admin_Dashboard.py")
    else:
        if st.sidebar.button("👤 Open Student Dashboard", use_container_width=True):
            st.switch_page("pages/3_👤_Student_Dashboard.py")

    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.user = None
        st.session_state.auth_role = None
        st.rerun()

st.sidebar.markdown("---")

# Redis Connection Status Banner
status = redis_service.get_status()
if status["connected"]:
    st.sidebar.success(status["message"])
else:
    st.sidebar.error(status["message"])

# --- MAIN LANDING PAGE CONTENT ---

# 1. TOP CENTER HEADER & INTRO
st.markdown("""
    <div class="hero-title">Real-Time Quiz Analytics and Leaderboard System Using Redis</div>
    <div class="hero-subtitle">Test your knowledge, track your performance, and compete on the live leaderboard.</div>
    <div class="hero-intro">
        Welcome to our real-time quiz platform. Take quizzes, get instant results, and see your ranking on the live leaderboard.
    </div>
""", unsafe_allow_html=True)

# 2. ROLE SELECTION ("CONTINUE AS") - FIRST
st.markdown('<div class="section-heading">Continue As</div>', unsafe_allow_html=True)

auth_role = st.session_state.get("auth_role")

if not auth_role:
    col_std, col_adm = st.columns(2)

    with col_std:
        st.markdown("""
            <div class="role-card">
                <h3 style="color:#2dd4bf; margin-top:0;">👨‍🎓 Student</h3>
                <p style="color:#cbd5e1; font-size:0.92rem;">Register, take quizzes, view instant scores & live rankings.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Continue as Student", key="btn_choose_student", use_container_width=True, type="primary"):
            st.session_state.auth_role = "student"
            st.rerun()

    with col_adm:
        st.markdown("""
            <div class="role-card">
                <h3 style="color:#f43f5e; margin-top:0;">⚙️ Admin</h3>
                <p style="color:#cbd5e1; font-size:0.92rem;">Manage quiz questions, inspect analytics & student performance.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Continue as Admin", key="btn_choose_admin", use_container_width=True):
            st.session_state.auth_role = "admin"
            st.rerun()

elif auth_role == "student":
    col_back, _ = st.columns([1, 3])
    with col_back:
        if st.button("⬅️ Change Role", key="btn_back_student"):
            st.session_state.auth_role = None
            st.rerun()

    tab_s_login, tab_s_reg = st.tabs(["🔑 Student Login", "📝 Register New Student"])

    with tab_s_login:
        st.markdown("""
            <div style="background: rgba(15,23,42,0.85); padding: 20px; border-radius: 12px; border: 1px solid rgba(45,212,191,0.25);">
                <h4 style="color:#2dd4bf; margin-top:0;">Student Sign In</h4>
                <p style="color:#94a3b8; font-size:0.85rem;">Demo account: <b>prachi</b> / <b>password123</b></p>
            </div>
        """, unsafe_allow_html=True)
        with st.form("std_login_form"):
            username = st.text_input("Username", value="prachi")
            password = st.text_input("Password", type="password", value="password123")
            submit = st.form_submit_button("Sign In as Student", use_container_width=True, type="primary")

            if submit:
                u_clean = username.strip().lower()
                u_info = redis_service.get_user(u_clean)
                name = u_info.get("name", u_clean.capitalize())
                st.session_state.user = {"username": u_clean, "name": name, "role": "student"}
                st.switch_page("pages/3_👤_Student_Dashboard.py")

    with tab_s_reg:
        st.markdown("""
            <div style="background: rgba(15,23,42,0.85); padding: 20px; border-radius: 12px; border: 1px solid rgba(45,212,191,0.25);">
                <h4 style="color:#34d399; margin-top:0;">New Student Registration</h4>
            </div>
        """, unsafe_allow_html=True)
        with st.form("std_reg_form"):
            reg_name = st.text_input("Full Name", placeholder="e.g. Shivam Kumar")
            reg_user = st.text_input("Choose Username", placeholder="e.g. shivam")
            reg_pass = st.text_input("Choose Password", type="password")
            reg_submit = st.form_submit_button("Register Account", use_container_width=True)

            if reg_submit:
                if not reg_name or not reg_user or not reg_pass:
                    st.error("All fields are required.")
                else:
                    reg_user_clean = reg_user.strip().lower()
                    existing = redis_service.get_user(reg_user_clean)
                    if existing:
                        st.error(f"Username '{reg_user_clean}' is already registered.")
                    else:
                        redis_service.save_user(reg_user_clean, reg_name.strip(), "student")
                        st.session_state.user = {"username": reg_user_clean, "name": reg_name.strip(), "role": "student"}
                        st.switch_page("pages/3_👤_Student_Dashboard.py")

elif auth_role == "admin":
    col_back, _ = st.columns([1, 3])
    with col_back:
        if st.button("⬅️ Change Role", key="btn_back_admin"):
            st.session_state.auth_role = None
            st.rerun()

    st.markdown("""
        <div style="background: rgba(15,23,42,0.85); padding: 20px; border-radius: 12px; border: 1px solid rgba(45,212,191,0.25);">
            <h4 style="color:#f43f5e; margin-top:0;">Admin Sign In</h4>
            <p style="color:#94a3b8; font-size:0.85rem;">Admin credentials: <b>admin</b> / <b>admin123</b></p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("adm_login_form"):
        adm_user = st.text_input("Admin Username", value="admin")
        adm_pass = st.text_input("Admin Password", type="password", value="admin123")
        adm_submit = st.form_submit_button("Sign In as Admin", use_container_width=True, type="primary")

        if adm_submit:
            if adm_user.strip().lower() == "admin" and adm_pass == "admin123":
                st.session_state.user = {"username": "admin", "name": "System Administrator", "role": "admin"}
                st.switch_page("pages/7_⚙_Admin_Dashboard.py")
            else:
                st.error("Invalid Admin credentials.")

# 3. QUIZ GUIDELINES CARD - SECOND (BELOW ROLE SELECTION)
st.markdown("""
    <div class="guidelines-card">
        <div class="guidelines-title">📋 Quiz Guidelines</div>
        <ul class="guidelines-list">
            <li>Read each question carefully.</li>
            <li>Select one answer for each question.</li>
            <li>Complete the quiz before the timer ends.</li>
            <li>Your score is calculated automatically.</li>
            <li>Your score will be added to the live leaderboard.</li>
            <li>Do not refresh the page during the quiz.</li>
        </ul>
    </div>
""", unsafe_allow_html=True)
