"""
Analytics Service Module
========================
Generates analytical statistics and interactive Plotly figures:
- KPI metrics (Total Participants, Attempts, Avg Score, Highest Score, Lowest Score, Active Participants)
- Interactive Plotly Charts (Score Distribution, Question Performance, Quiz Performance, Participation, Leaderboard)
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
from services.quiz_service import quiz_service
from services.redis_service import redis_service

class AnalyticsService:
    def get_kpi_summary(self) -> Dict[str, Any]:
        """Calculates global KPI metrics combining Redis active state & historical attempt data."""
        attempts = quiz_service.attempts
        quizzes = quiz_service.get_all_quizzes()

        total_attempts = len(attempts)
        unique_participants = len(set(a["username"] for a in attempts)) if attempts else 0

        scores = [a["score"] for a in attempts]
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0

        # Active participants from Redis Set
        active_participants = redis_service.get_active_count("all")

        return {
            "total_participants": unique_participants,
            "total_attempts": total_attempts,
            "avg_score": avg_score,
            "highest_score": max_score,
            "lowest_score": min_score,
            "active_participants": active_participants,
            "total_quizzes": len(quizzes)
        }

    def get_score_distribution_chart(self, quiz_id: str = "all") -> go.Figure:
        """Plotly chart: Score Distribution (Histogram / Bar chart)."""
        attempts = quiz_service.attempts
        if quiz_id != "all":
            attempts = [a for a in attempts if a["quiz_id"] == quiz_id]

        if not attempts:
            fig = go.Figure()
            fig.update_layout(title="No attempt data available", template="plotly_dark")
            return fig

        df = pd.DataFrame(attempts)
        fig = px.histogram(
            df,
            x="score",
            nbins=11,
            title="Score Distribution across Quiz Attempts",
            labels={"score": "Score (Marks)", "count": "Frequency"},
            color_discrete_sequence=["#818cf8"],
            template="plotly_dark"
        )
        fig.update_layout(
            bargap=0.1,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#f8fafc")
        )
        return fig

    def get_question_performance_chart(self, quiz_id: str) -> go.Figure:
        """Plotly chart: Question-wise Accuracy (% correct)."""
        questions = quiz_service.get_questions_for_quiz(quiz_id)
        if not questions:
            fig = go.Figure()
            fig.update_layout(title="No questions found for this quiz", template="plotly_dark")
            return fig

        data = []
        for i, q in enumerate(questions, 1):
            stats = redis_service.get_question_stats(quiz_id, q["id"])
            total = stats["total_attempts"]
            correct = stats["correct_attempts"]
            pct = round((correct / total) * 100, 1) if total > 0 else 0.0

            # Fallback to attempts log if Redis analytics not populated
            if total == 0:
                attempts = [a for a in quiz_service.attempts if a["quiz_id"] == quiz_id]
                for a in attempts:
                    ans = a.get("answers", {}).get(q["id"])
                    if ans:
                        total += 1
                        if ans == q["correct_answer"]:
                            correct += 1
                pct = round((correct / total) * 100, 1) if total > 0 else 0.0

            data.append({
                "Question": f"Q{i}",
                "Accuracy (%)": pct,
                "Text": q["question"][:30] + "..."
            })

        df = pd.DataFrame(data)
        fig = px.bar(
            df,
            x="Question",
            y="Accuracy (%)",
            hover_data=["Text"],
            title=f"Question-wise Accuracy Percentage",
            color="Accuracy (%)",
            color_continuous_scale="Viridis",
            template="plotly_dark"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#f8fafc")
        )
        return fig

    def get_quiz_performance_chart(self) -> go.Figure:
        """Plotly chart: Quiz Performance Comparison (Average scores per quiz)."""
        quizzes = quiz_service.get_all_quizzes()
        attempts = quiz_service.attempts

        data = []
        for q in quizzes:
            q_attempts = [a for a in attempts if a["quiz_id"] == q["id"]]
            avg = round(sum(a["score"] for a in q_attempts) / len(q_attempts), 2) if q_attempts else 0.0
            data.append({
                "Quiz Title": q["title"],
                "Average Score": avg,
                "Attempts": len(q_attempts)
            })

        df = pd.DataFrame(data)
        fig = px.bar(
            df,
            x="Quiz Title",
            y="Average Score",
            color="Quiz Title",
            title="Average Score by Quiz Category",
            template="plotly_dark"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#f8fafc")
        )
        return fig

    def get_participation_chart(self) -> go.Figure:
        """Plotly chart: Participation Share per Quiz (Donut chart)."""
        quizzes = quiz_service.get_all_quizzes()
        attempts = quiz_service.attempts

        data = []
        for q in quizzes:
            count = len([a for a in attempts if a["quiz_id"] == q["id"]])
            data.append({"Quiz Title": q["title"], "Attempts": count})

        df = pd.DataFrame(data)
        fig = px.pie(
            df,
            names="Quiz Title",
            values="Attempts",
            hole=0.4,
            title="Quiz Participation Breakdown",
            template="plotly_dark"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#f8fafc")
        )
        return fig

    def get_top_leaderboard_chart(self, quiz_id: str = "overall") -> go.Figure:
        """Plotly chart: Top 5 Performers Bar Chart."""
        raw_leaderboard = redis_service.get_leaderboard(quiz_id, top_n=5)
        if not raw_leaderboard:
            fig = go.Figure()
            fig.update_layout(title="No leaderboard data available", template="plotly_dark")
            return fig

        data = [{"Student": user, "Score": score} for user, score in raw_leaderboard]
        df = pd.DataFrame(data)

        fig = px.bar(
            df,
            x="Score",
            y="Student",
            orientation="h",
            title="Top 5 Performers",
            color="Score",
            color_continuous_scale="Purples",
            template="plotly_dark"
        )
        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#f8fafc")
        )
        return fig

analytics_service = AnalyticsService()
