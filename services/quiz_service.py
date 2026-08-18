"""
Quiz Service Module
===================
Manages quiz CRUD operations, question banks, student quiz session state,
score evaluation, duplicate submission prevention, and Redis real-time score publishing.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import QUIZZES_FILE, QUESTIONS_FILE, ATTEMPTS_FILE
from services.redis_service import redis_service

class QuizService:
    def __init__(self):
        self._load_all()

    def _load_all(self):
        self.quizzes = self._read_json(QUIZZES_FILE)
        self.questions = self._read_json(QUESTIONS_FILE)
        self.attempts = self._read_json(ATTEMPTS_FILE)

    def _read_json(self, path) -> List[Dict[str, Any]]:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _write_json(self, path, data: List[Dict[str, Any]]):
        path.parent.mkdir(exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # --- Quiz CRUD ---
    def get_all_quizzes(self) -> List[Dict[str, Any]]:
        self._load_all()
        return self.quizzes

    def get_quiz_by_id(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        self._load_all()
        return next((q for q in self.quizzes if q["id"] == quiz_id), None)

    def create_quiz(self, title: str, description: str, duration_minutes: int) -> Dict[str, Any]:
        self._load_all()
        new_id = f"quiz_{uuid.uuid4().hex[:8]}"
        new_quiz = {
            "id": new_id,
            "title": title,
            "description": description,
            "duration_minutes": duration_minutes,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pass_percentage": 60
        }
        self.quizzes.append(new_quiz)
        self._write_json(QUIZZES_FILE, self.quizzes)
        return new_quiz

    # --- Questions CRUD ---
    def get_questions_for_quiz(self, quiz_id: str) -> List[Dict[str, Any]]:
        self._load_all()
        return [q for q in self.questions if q["quiz_id"] == quiz_id]

    def add_question(self, quiz_id: str, question_text: str, options: List[str], correct_answer: str) -> Dict[str, Any]:
        self._load_all()
        new_id = f"q_{uuid.uuid4().hex[:8]}"
        new_q = {
            "id": new_id,
            "quiz_id": quiz_id,
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer
        }
        self.questions.append(new_q)
        self._write_json(QUESTIONS_FILE, self.questions)
        return new_q

    def update_question(self, question_id: str, question_text: str, options: List[str], correct_answer: str) -> bool:
        self._load_all()
        for q in self.questions:
            if q["id"] == question_id:
                q["question"] = question_text
                q["options"] = options
                q["correct_answer"] = correct_answer
                self._write_json(QUESTIONS_FILE, self.questions)
                return True
        return False

    def delete_question(self, question_id: str) -> bool:
        self._load_all()
        initial_len = len(self.questions)
        self.questions = [q for q in self.questions if q["id"] != question_id]
        if len(self.questions) < initial_len:
            self._write_json(QUESTIONS_FILE, self.questions)
            return True
        return False

    # --- Active Quiz Session Management ---
    def start_quiz_session(self, username: str, quiz_id: str) -> Dict[str, Any]:
        """
        [REDIS SESSION & ACTIVE PARTICIPANTS]
        Registers student session in Redis Hashes and adds student to active Redis Set.
        """
        quiz = self.get_quiz_by_id(quiz_id)
        if not quiz:
            return {"success": False, "message": "Quiz not found."}

        # Check duplicate submission check
        if self.has_user_attempted(username, quiz_id):
            return {"success": False, "message": "You have already submitted this quiz."}

        now_ts = datetime.now().timestamp()
        session_data = {
            "quiz_id": quiz_id,
            "username": username,
            "start_time": now_ts,
            "status": "in_progress",
            "duration_seconds": quiz["duration_minutes"] * 60
        }

        # Store session in Redis Hash & Active Participant Set
        redis_service.set_user_session(username, session_data)
        redis_service.add_active_participant(quiz_id, username)

        return {"success": True, "session": session_data}

    def has_user_attempted(self, username: str, quiz_id: str) -> bool:
        """Checks whether the user has already completed this quiz."""
        # 1. Check Redis Score Hash or Leaderboard score
        score = redis_service.get_user_score(quiz_id, username)
        if score is not None:
            return True

        # 2. Check JSON attempts fallback
        self._load_all()
        return any(a["username"] == username and a["quiz_id"] == quiz_id for a in self.attempts)

    # --- Quiz Submission & Automatic Evaluation ---
    def submit_quiz(self, username: str, quiz_id: str, student_answers: Dict[str, str], time_taken_seconds: int) -> Dict[str, Any]:
        """
        Evaluates student answers:
        1. Compares each answer with answer key.
        2. Calculates total correct answers & score percentage.
        3. Updates Redis Sorted Set leaderboard (`ZADD`).
        4. Updates question performance counters in Redis (`HINCRBY`).
        5. Removes student from active Redis set (`SREM`).
        6. Clears active session state from Redis.
        7. Saves attempt details to attempts.json.
        """
        if self.has_user_attempted(username, quiz_id):
            return {"success": False, "message": "Duplicate submission detected. Quiz already submitted."}

        questions = self.get_questions_for_quiz(quiz_id)
        if not questions:
            return {"success": False, "message": "No questions found for this quiz."}

        score = 0
        total_q = len(questions)

        for q in questions:
            q_id = q["id"]
            user_ans = student_answers.get(q_id, "")
            is_correct = (user_ans == q["correct_answer"])
            if is_correct:
                score += 1
            # Update Redis question analytics
            redis_service.incr_question_stat(quiz_id, q_id, is_correct)

        percentage = round((score / total_q) * 100, 2) if total_q > 0 else 0.0

        # Save Attempt Record
        attempt_record = {
            "attempt_id": f"att_{uuid.uuid4().hex[:8]}",
            "username": username,
            "quiz_id": quiz_id,
            "score": score,
            "total_questions": total_q,
            "percentage": percentage,
            "time_taken_seconds": time_taken_seconds,
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "answers": student_answers
        }

        self.attempts.append(attempt_record)
        self._write_json(ATTEMPTS_FILE, self.attempts)

        # REDIS CORE OPERATIONS:
        # Update Redis Sorted Set for Live Leaderboard
        redis_service.update_leaderboard_score(quiz_id, username, score)

        # Remove from active participants set & clear active session
        redis_service.remove_active_participant(quiz_id, username)
        redis_service.clear_user_session(username)

        return {
            "success": True,
            "attempt": attempt_record,
            "message": f"Quiz submitted successfully! Score: {score}/{total_q} ({percentage}%)"
        }

    def get_user_attempts(self, username: str) -> List[Dict[str, Any]]:
        self._load_all()
        return [a for a in self.attempts if a["username"] == username]

quiz_service = QuizService()
