# Real-Time Quiz Analytics and Leaderboard System Using Redis

A simple, clean, and fully functional college project built with **Python**, **Streamlit**, **Redis**, **Plotly**, and **JSON**.

---

## 🎯 Project Objective

Traditional relational databases require expensive SQL queries (`SELECT name, SUM(score) FROM attempts GROUP BY name ORDER BY score DESC`) to rank students. As submission volume grows, scanning database tables repeatedly causes high IOPS, latency, and database locks.

By utilizing **Redis Sorted Sets (`ZADD`, `ZREVRANGE`, `ZREVRANK`)**, score updates and live leaderboard rank calculations are executed in **$O(\log N)$ time**, allowing instant score storage and sub-millisecond leaderboard retrieval directly from memory.

---

## ✨ Features

1. **User Authentication (Student & Admin)**:
   - Student registration & login.
   - Separate Admin login.
   - User profiles saved in Redis Hashes (`user:<username>`).

2. **Interactive Quiz Module**:
   - 2 sample quizzes (*Python Basics* and *Data Structures*) with 10 questions each.
   - 4 options per multiple-choice question.
   - Simple countdown timer badge.
   - Automated instant score calculation.

3. **Redis Real-Time Core Module**:
   - **Sorted Sets (ZSET)**: Live leaderboard rankings (`leaderboard:<quiz_id>`).
   - **Hashes (HASH)**: User profiles (`user:<username>`) & active quiz sessions (`session:<username>`).
   - **Sets (SET)**: Active participant tracking (`active_participants`).

4. **Live Leaderboard Page**:
   - Ranking table displaying `Rank | Student | Score`.
   - Highest score automatically appears at the top.
   - Reads scores directly from Redis Sorted Sets using `ZREVRANGE`.
   - Highlights current student's live rank and score.

5. **Result Evaluation Page**:
   - Displays Quiz Name, Score (`8/10`), Correct count, Wrong count, Percentage, and Live Rank fetched from Redis.

6. **Admin Analytics Dashboard**:
   - **KPI Cards**: Total Participants, Total Quiz Attempts, Average Score, Highest Score, Lowest Score.
   - **4 Plotly Visualizations**:
     - Score Distribution Histogram
     - Average Score by Quiz Category
     - Question-wise Correct Answer %
     - Top 5 High Scoring Students
   - **Question Bank Manager**: View, add, edit, and delete questions.

---

## 📁 Project Architecture & Layout

```
real_time_quiz/
├── app.py                      # Main entry point & fresh UI theme setup
├── requirements.txt            # Python dependencies (streamlit, redis, plotly, pandas, python-dotenv)
├── README.md                   # Setup guide & viva Redis CLI commands
├── .env.example                # Environment configuration template
├── .env                        # Redis host and port settings
│
├── data/
│   └── quizzes.json            # Sample quizzes metadata & 10 questions per quiz
│
├── pages/                      # Native Streamlit pages
│   ├── 1_📝_Register.py        # Student registration form
│   ├── 2_🔑_Login.py           # Student & Admin login portal
│   ├── 3_👤_Student_Dashboard.py# Student rank spotlight & attempt summary
│   ├── 4_📚_Quiz.py            # Quiz selector, 10 MCQs, countdown timer, auto score
│   ├── 5_📊_Result.py          # Score evaluation card (8/10) & Redis rank
│   ├── 6_🏆_Live_Leaderboard.py# Live table reading directly from Redis Sorted Sets
│   └── 7_⚙_Admin_Dashboard.py # Admin KPI cards, 4 Plotly charts & Question manager
│
└── services/
    └── redis_service.py        # Real Redis connection (localhost:6379) & data structures
```

---

## ⚡ Redis Data Structures Explained (For Viva)

| Feature | Redis Data Structure | Redis Commands Used | Description |
|---|---|---|---|
| **Live Leaderboards** | Sorted Set (ZSET) | `ZADD`, `ZREVRANGE`, `ZREVRANK`, `ZSCORE` | Stores student scores and automatically orders highest score first in $O(\log N)$ time. |
| **User Profiles & Sessions** | Hash (HASH) | `HSET`, `HGETALL`, `HDEL` | Stores user field-value attributes (`name`, `role`) and active quiz session metadata. |
| **Active Participants** | Set (SET) | `SADD`, `SREM`, `SCARD` | Tracks unique students currently attempting a quiz. |

---

## 🚀 Step-by-Step Installation & Setup

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start Redis Server on localhost:6379

#### Option A: Docker (Recommended)
```bash
docker run --name redis-quiz -p 6379:6379 -d redis
```

#### Option B: Windows Native Redis / WSL
Launch `redis-server.exe` on port `6379`.

### Step 3: Run the Streamlit Application
```bash
streamlit run app.py
```

The application will open automatically at `http://localhost:8501`.

---

## 🔍 How to Verify Redis in Terminal / Command Prompt

### 1. Test Redis Connection
```bash
redis-cli ping
```
**Expected Output**:
```text
PONG
```

### 2. View All Stored Keys in Redis
```bash
redis-cli KEYS "*"
```

### 3. Inspect Live Leaderboard Sorted Set Data
```bash
# View overall leaderboard
redis-cli ZREVRANGE leaderboard:overall 0 -1 WITHSCORES

# View Python Basics leaderboard
redis-cli ZREVRANGE leaderboard:quiz_python_basics 0 -1 WITHSCORES
```

### 4. Inspect User Profile Hash
```bash
redis-cli HGETALL user:prachi
```

---

## 🎓 Viva Demonstration Walkthrough (For College Faculty)

1. **Start Redis Server**: Ensure `redis-cli ping` returns `PONG`.
2. **Launch Streamlit App**: Run `streamlit run app.py` and point to the status banner: **`🟢 Redis Connected (localhost:6379)`**.
3. **Register/Login as Student**:
   - Log in as `prachi` / `password123`.
4. **Take Quiz**:
   - Open **4 Quiz** → Select *Python Basics*.
   - Answer the 10 questions and click **Submit Quiz**.
5. **Score Generated & Saved to Redis**:
   - Open **5 Result** → Show score card (`Score: 9/10, Correct: 9, Wrong: 1, Percentage: 90%`).
6. **Live Leaderboard Update**:
   - Open **6 Live Leaderboard** → Show live student ranking populated directly from Redis Sorted Sets (`ZREVRANGE`).
7. **Verify via Redis CLI**:
   - Open terminal and run `redis-cli ZREVRANGE leaderboard:quiz_python_basics 0 -1 WITHSCORES`.
   - Show faculty the exact matching score stored in Redis memory!
8. **Admin Dashboard**:
   - Log in as `admin` / `admin123`.
   - Open **7 Admin Dashboard** to display KPI metrics, 4 Plotly charts, and question manager.
