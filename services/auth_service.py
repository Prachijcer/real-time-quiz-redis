"""
Authentication Service Module
==============================
Handles user registration, authentication, password security,
role checking (Student vs Admin), and syncing user credentials to Redis.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from config import USERS_FILE
from services.redis_service import redis_service

def hash_password(password: str) -> str:
    """Returns SHA-256 hex digest of the password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class AuthService:
    def __init__(self):
        self._load_users()

    def _load_users(self) -> List[Dict[str, Any]]:
        if USERS_FILE.exists():
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    self.users = json.load(f)
            except Exception:
                self.users = []
        else:
            self.users = []
        return self.users

    def _save_users(self):
        USERS_FILE.parent.mkdir(exist_ok=True)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=2)

    def register_user(self, username: str, name: str, password: str) -> Dict[str, Any]:
        """
        Registers a new student user.
        - Validates non-empty input fields.
        - Checks for duplicate username.
        - Hashes password.
        - Saves to users.json and stores in Redis Hash `user:<username>`.
        """
        username = username.strip().lower()
        name = name.strip()

        if not username or not name or not password:
            return {"success": False, "message": "All fields are required."}

        if len(username) < 3:
            return {"success": False, "message": "Username must be at least 3 characters."}

        # Check duplicate username
        self._load_users()
        if any(u["username"].lower() == username for u in self.users):
            return {"success": False, "message": f"Username '{username}' is already taken."}

        pwd_hash = hash_password(password)
        new_user = {
            "username": username,
            "password_hash": pwd_hash,
            "name": name,
            "role": "student",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.users.append(new_user)
        self._save_users()

        # Sync user profile into Redis Hash (HSET user:<username>)
        if redis_service.client:
            redis_service.client.hset(
                f"user:{username}",
                mapping={
                    "name": name,
                    "role": "student",
                    "created_at": new_user["created_at"]
                }
            )

        return {"success": True, "user": new_user, "message": "Registration successful!"}

    def authenticate_user(self, username: str, password: str, expected_role: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticates a user against credentials in users.json & Redis.
        Optionally verifies expected_role ('student' or 'admin').
        """
        username = username.strip().lower()
        if not username or not password:
            return {"success": False, "message": "Please enter username and password."}

        self._load_users()
        pwd_hash = hash_password(password)

        user = next((u for u in self.users if u["username"].lower() == username), None)

        if not user:
            return {"success": False, "message": "Invalid username or password."}

        if user["password_hash"] != pwd_hash:
            return {"success": False, "message": "Invalid username or password."}

        if expected_role and user.get("role") != expected_role:
            return {"success": False, "message": f"Access denied. User is not an {expected_role}."}

        return {"success": True, "user": user, "message": f"Welcome back, {user['name']}!"}

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        self._load_users()
        return next((u for u in self.users if u["username"].lower() == username.lower()), None)

auth_service = AuthService()
