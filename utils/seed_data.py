"""
Data Seeder Module
==================
Populates initial sample user profiles, quiz attempts, question statistics,
and Redis Sorted Sets (`ZADD`) on app startup.
"""

import json
import logging
from config import USERS_FILE, ATTEMPTS_FILE, QUESTIONS_FILE
from services.redis_service import redis_service

logger = logging.getLogger(__name__)

def seed_redis_data():
    """Seeds Redis Hashes, Sets, and Sorted Sets from JSON data files."""
    if not redis_service.client:
        logger.warning("Redis client unavailable for seeding.")
        return

    logger.info("Seeding initial data into Redis...")

    # 1. Seed Users into Redis Hashes
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
                for u in users:
                    username = u["username"]
                    redis_service.client.hset(
                        f"user:{username}",
                        mapping={
                            "name": u["name"],
                            "role": u["role"],
                            "created_at": u.get("created_at", "")
                        }
                    )
        except Exception as e:
            logger.error(f"Error seeding user hashes: {e}")

    # 2. Seed Attempts & Leaderboard Sorted Sets
    if ATTEMPTS_FILE.exists():
        try:
            with open(ATTEMPTS_FILE, "r", encoding="utf-8") as f:
                attempts = json.load(f)
                for a in attempts:
                    username = a["username"]
                    quiz_id = a["quiz_id"]
                    score = float(a["score"])

                    # Update Redis Sorted Set for quiz leaderboard
                    redis_service.client.zadd(f"leaderboard:{quiz_id}", {username: score})

                    # Update overall leaderboard score
                    current = redis_service.client.zscore("leaderboard:overall", username) or 0
                    redis_service.client.zadd("leaderboard:overall", {username: float(current) + score})

                    # Update question accuracy stats
                    answers = a.get("answers", {})
                    for q_id, ans in answers.items():
                        # We increment attempts counter
                        redis_service.client.hincrby(f"analytics:question:{quiz_id}:{q_id}", "total_attempts", 1)

                        # Check correctness from questions file
                        correct_ans = _get_correct_answer(q_id)
                        if ans == correct_ans:
                            redis_service.client.hincrby(f"analytics:question:{quiz_id}:{q_id}", "correct_attempts", 1)

        except Exception as e:
            logger.error(f"Error seeding leaderboard sorted sets: {e}")

    logger.info("Redis seeding complete!")

def _get_correct_answer(question_id: str) -> str:
    if QUESTIONS_FILE.exists():
        try:
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                questions = json.load(f)
                for q in questions:
                    if q["id"] == question_id:
                        return q["correct_answer"]
        except Exception:
            pass
    return ""

if __name__ == "__main__":
    seed_redis_data()
    print("Seed execution finished successfully.")
