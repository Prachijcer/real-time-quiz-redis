import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        /* Modern Glassmorphism & Custom Styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            color: #f8fafc;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }

        /* Card styles */
        .quiz-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        }

        .quiz-card:hover {
            transform: translateY(-4px);
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.2);
        }

        .stat-card {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #6366f1;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #818cf8;
            margin-top: 4px;
        }

        .stat-label {
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
        }

        /* Badge Pills */
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .badge-success { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
        .badge-info { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
        .badge-warning { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-purple { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }

        /* Timer badge */
        .timer-box {
            background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 1.5rem;
            font-weight: 800;
            text-align: center;
            letter-spacing: 0.1em;
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }

        /* Leaderboard rank highlight */
        .user-rank-highlight {
            background: rgba(99, 102, 241, 0.25) !important;
            border-left: 4px solid #818cf8 !important;
        }

        /* Header styling */
        .page-header {
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }

        .page-title {
            font-size: 2.25rem;
            font-weight: 800;
            background: linear-gradient(90deg, #818cf8 0%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }

        .page-subtitle {
            color: #94a3b8;
            font-size: 1rem;
        }

        /* Custom buttons */
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        </style>
    """, unsafe_allow_html=True)

def render_page_header(title: str, subtitle: str, icon: str = "⚡"):
    st.markdown(f"""
        <div class="page-header">
            <div class="page-title">{icon} {title}</div>
            <div class="page-subtitle">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)

def render_stat_card(label: str, value, border_color: str = "#6366f1"):
    st.markdown(f"""
        <div class="stat-card" style="border-left-color: {border_color};">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)
