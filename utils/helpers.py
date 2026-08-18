import streamlit as st
import json
import logging
from config import USERS_FILE, ATTEMPTS_FILE, QUESTIONS_FILE

logger = logging.getLogger(__name__)

def inject_custom_css():
    """Injects clean, modern CSS styling into Streamlit."""
    st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1100px;
        }
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            color: #f8fafc;
        }
        .quiz-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        }
        .stat-card {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 10px;
            padding: 16px;
            border-left: 4px solid #6366f1;
        }
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #818cf8;
        }
        .stat-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            color: #94a3b8;
        }
        .timer-box {
            background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 1.4rem;
            font-weight: 800;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

def render_page_header(title: str, subtitle: str, icon: str = "⚡"):
    """Displays a clean header on each page."""
    st.markdown(f"""
        <div style="border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px; margin-bottom: 20px;">
            <h1 style="font-size: 2rem; color: #818cf8; margin: 0;">{icon} {title}</h1>
            <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 4px;">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def render_stat_card(label: str, value, color: str = "#6366f1"):
    """Displays a KPI metric card."""
    st.markdown(f"""
        <div class="stat-card" style="border-left-color: {color};">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)

def seed_redis_data():
    """Populates initial sample user profiles & scores into Redis."""
    from services.redis_service import redis_service
    if not redis_service.client:
        return

    # Seed users into Redis Hashes
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
                for u in users:
                    redis_service.client.hset(
                        f"user:{u['username']}",
                        mapping={"name": u["name"], "role": u["role"]}
                    )
        except Exception:
            pass

    # Seed attempts into Redis Sorted Sets
    if ATTEMPTS_FILE.exists():
        try:
            with open(ATTEMPTS_FILE, "r", encoding="utf-8") as f:
                attempts = json.load(f)
                for a in attempts:
                    redis_service.update_leaderboard_score(a["quiz_id"], a["username"], float(a["score"]))
        except Exception:
            pass
