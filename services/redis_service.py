"""
===================================================================
SERVICES / REDIS_SERVICE.PY
===================================================================
Real Redis Client implementation for College Project Demonstration.

This module connects directly to a live Redis server running locally on:
Host: localhost
Port: 6379

Demonstrates Essential Redis Data Structures:
1. REDIS SORTED SETS (ZSET) -> Live Leaderboard (ZADD, ZREVRANGE, ZREVRANK, ZSCORE)
2. REDIS HASHES (HASH)      -> User Profiles & Active Sessions (HSET, HGETALL)
3. REDIS SETS (SET)         -> Active Participants Tracking (SADD, SREM, SCARD)
4. REDIS LISTS (LIST)       -> Student Quiz Attempt History (LPUSH, LRANGE)
"""

import os
import json
import time
import logging
from typing import List, Dict, Tuple, Optional, Any
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
if REDIS_PASSWORD == "":
    REDIS_PASSWORD = None
REDIS_DB = int(os.getenv("REDIS_DB", 0))

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.client = None
        self.is_connected = False
        self.connection_message = ""
        self.connect()

    def connect(self):
        """Connects directly to the real Redis server on localhost:6379."""
        try:
            r = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0
            )
            r.ping()
            self.client = r
            self.is_connected = True
            self.connection_message = f"🟢 Redis Connected ({REDIS_HOST}:{REDIS_PORT})"
        except Exception as e:
            self.client = None
            self.is_connected = False
            self.connection_message = f"🔴 Redis is not running. Please start the Redis server (host: {REDIS_HOST}, port: {REDIS_PORT})."

    def get_status(self) -> Dict[str, Any]:
        """Returns connection health and status message for Streamlit UI."""
        if self.client:
            try:
                self.client.ping()
                self.is_connected = True
                self.connection_message = f"🟢 Redis Connected ({REDIS_HOST}:{REDIS_PORT})"
            except Exception:
                self.is_connected = False
                self.connection_message = f"🔴 Redis is not running. Please start the Redis server (host: {REDIS_HOST}, port: {REDIS_PORT})."
        else:
            self.connect()
            
        return {
            "connected": self.is_connected,
            "message": self.connection_message,
            "host": REDIS_HOST,
            "port": REDIS_PORT
        }

    # =====================================================================
    # 1. REDIS SORTED SETS (ZSET) -> Live Leaderboard Operations
    # =====================================================================

    def save_score(self, quiz_id: str, username: str, score: float):
        """[REDIS ZADD] Stores student score into Redis Sorted Set."""
        if not self.is_connected or not self.client:
            return

        # Quiz-specific leaderboard
        self.client.zadd(f"leaderboard:{quiz_id}", {username: float(score)})

        # Overall cumulative leaderboard
        current = self.client.zscore("leaderboard:overall", username) or 0
        self.client.zadd("leaderboard:overall", {username: float(current) + float(score)})

    def get_leaderboard(self, quiz_id: str = "overall", top_n: int = 50) -> List[Tuple[str, float]]:
        """[REDIS ZREVRANGE] Retrieves top scores in descending order directly from Redis."""
        if not self.is_connected or not self.client:
            return []
        key = f"leaderboard:{quiz_id}" if quiz_id != "overall" else "leaderboard:overall"
        return self.client.zrevrange(key, 0, top_n - 1, withscores=True)

    def get_user_rank(self, quiz_id: str, username: str) -> Optional[int]:
        """[REDIS ZREVRANK] Retrieves 1-based rank position of a student."""
        if not self.is_connected or not self.client:
            return None
        key = f"leaderboard:{quiz_id}" if quiz_id != "overall" else "leaderboard:overall"
        rank_0 = self.client.zrevrank(key, username)
        return (rank_0 + 1) if rank_0 is not None else None

    def get_user_score(self, quiz_id: str, username: str) -> Optional[float]:
        """[REDIS ZSCORE] Retrieves score of a student from Redis Sorted Set."""
        if not self.is_connected or not self.client:
            return None
        key = f"leaderboard:{quiz_id}" if quiz_id != "overall" else "leaderboard:overall"
        score = self.client.zscore(key, username)
        return float(score) if score is not None else None

    def delete_quiz_leaderboard(self, quiz_id: str):
        """[REDIS DEL] Deletes quiz leaderboard key from Redis."""
        if self.is_connected and self.client:
            self.client.delete(f"leaderboard:{quiz_id}")

    # =====================================================================
    # 2. REDIS HASHES (HASH) -> User Information & Session Metadata
    # =====================================================================

    def save_user(self, username: str, name: str, role: str = "student"):
        """[REDIS HSET] Stores user profile information in Redis Hash."""
        if self.is_connected and self.client:
            self.client.hset(f"user:{username}", mapping={"name": name, "role": role})

    def get_user(self, username: str) -> Dict[str, str]:
        """[REDIS HGETALL] Retrieves user profile fields from Redis Hash."""
        if not self.is_connected or not self.client:
            return {}
        return self.client.hgetall(f"user:{username}")

    def save_session(self, username: str, quiz_id: str, start_time: float):
        """[REDIS HSET] Stores active quiz session details in Redis Hash."""
        if self.is_connected and self.client:
            self.client.hset(
                f"session:{username}",
                mapping={"quiz_id": quiz_id, "start_time": str(start_time), "status": "active"}
            )

    def get_session(self, username: str) -> Dict[str, str]:
        """[REDIS HGETALL] Retrieves active quiz session details."""
        if not self.is_connected or not self.client:
            return {}
        return self.client.hgetall(f"session:{username}")

    def clear_session(self, username: str):
        """[REDIS DEL] Removes session key upon quiz completion."""
        if self.is_connected and self.client:
            self.client.delete(f"session:{username}")

    # =====================================================================
    # 3. REDIS SETS (SET) -> Active Users Tracking
    # =====================================================================

    def add_active_participant(self, username: str):
        """[REDIS SADD] Adds student to set of active participants."""
        if self.is_connected and self.client:
            self.client.sadd("active_participants", username)

    def remove_active_participant(self, username: str):
        """[REDIS SREM] Removes student from active participants set."""
        if self.is_connected and self.client:
            self.client.srem("active_participants", username)

    def get_active_participant_count(self) -> int:
        """[REDIS SCARD] Gets total count of active participants."""
        if not self.is_connected or not self.client:
            return 0
        return self.client.scard("active_participants")

    def get_active_participants(self) -> List[str]:
        """[REDIS SMEMBERS] Gets set members of active participants."""
        if not self.is_connected or not self.client:
            return []
        return list(self.client.smembers("active_participants"))

    # =====================================================================
    # 4. REDIS LISTS (LIST) -> Student Quiz Attempt History
    # =====================================================================

    def record_attempt(self, username: str, quiz_title: str, score: float, total_questions: int):
        """[REDIS LPUSH] Pushes student attempt record into Redis List."""
        if not self.is_connected or not self.client:
            return
        attempt_obj = json.dumps({
            "quiz": quiz_title,
            "score": f"{int(score)}/{total_questions}",
            "percentage": f"{int((score/total_questions)*100)}%",
            "date": time.strftime("%d %b %Y %H:%M"),
            "status": "Completed"
        })
        self.client.lpush(f"attempts:{username}", attempt_obj)

    def get_user_attempts(self, username: str) -> List[Dict[str, Any]]:
        """[REDIS LRANGE] Fetches attempt history for student from Redis List."""
        if not self.is_connected or not self.client:
            return []
        raw_list = self.client.lrange(f"attempts:{username}", 0, -1)
        attempts = []
        for item in raw_list:
            try:
                attempts.append(json.loads(item))
            except Exception:
                pass
        return attempts

    # =====================================================================
    # 5. RAW REDIS DATA INSPECTOR (FOR COLLEGE FACULTY VIVA DEMO)
    # =====================================================================

    def get_all_keys(self) -> List[str]:
        """[REDIS KEYS] Fetches all keys currently stored in Redis memory."""
        if not self.is_connected or not self.client:
            return []
        try:
            return [k for k in self.client.keys("*")]
        except Exception:
            return []

    def get_key_info(self, key: str) -> Dict[str, Any]:
        """Inspects key type and raw stored data directly from Redis memory."""
        if not self.is_connected or not self.client:
            return {"key": key, "type": "none", "value": None}
        try:
            key_type = self.client.type(key)
            val = None
            if key_type == "zset":
                val = self.client.zrevrange(key, 0, -1, withscores=True)
            elif key_type == "hash":
                val = self.client.hgetall(key)
            elif key_type == "set":
                val = list(self.client.smembers(key))
            elif key_type == "list":
                val = self.client.lrange(key, 0, -1)
            elif key_type == "string":
                val = self.client.get(key)
            return {"key": key, "type": key_type, "value": val}
        except Exception as e:
            return {"key": key, "type": "unknown", "value": str(e)}

# Singleton Instance
redis_service = RedisService()
