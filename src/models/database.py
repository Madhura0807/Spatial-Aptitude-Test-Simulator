"""
database.py
SQLite persistence layer. Owns the schema and every query used by the
application: Users, Scores, Quiz History, Question History, Achievements.
"""

import os
import sqlite3
from datetime import datetime

from src import config


class DatabaseManager:
    """Thin wrapper around sqlite3 providing typed helper methods for the
    application's controllers. One instance is shared app-wide."""

    def __init__(self, db_path=None):
        self.db_path = db_path or config.DATABASE_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------
    def _create_tables(self):
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                accuracy REAL NOT NULL,
                avg_response_time REAL NOT NULL,
                highest_streak INTEGER NOT NULL,
                difficulty TEXT NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES Users(id)
            );

            CREATE TABLE IF NOT EXISTS QuizHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quiz_date TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                time_taken REAL NOT NULL,
                difficulty TEXT NOT NULL,
                mode TEXT NOT NULL DEFAULT 'Quiz',
                FOREIGN KEY (user_id) REFERENCES Users(id)
            );

            CREATE TABLE IF NOT EXISTS QuestionHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_history_id INTEGER NOT NULL,
                shape_name TEXT NOT NULL,
                rotation_angle INTEGER NOT NULL,
                direction TEXT NOT NULL,
                correct INTEGER NOT NULL,
                response_time REAL NOT NULL,
                FOREIGN KEY (quiz_history_id) REFERENCES QuizHistory(id)
            );

            CREATE TABLE IF NOT EXISTS Achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_name TEXT NOT NULL,
                description TEXT,
                date_earned TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES Users(id)
            );
            """
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    def get_or_create_user(self, username="Guest"):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Users WHERE username = ?", (username,))
        row = cur.fetchone()
        if row:
            return dict(row)
        cur.execute(
            "INSERT INTO Users (username, created_at) VALUES (?, ?)",
            (username, datetime.now().isoformat()),
        )
        self.conn.commit()
        return {"id": cur.lastrowid, "username": username,
                "created_at": datetime.now().isoformat()}

    # ------------------------------------------------------------------
    # Quiz / Score persistence
    # ------------------------------------------------------------------
    def save_quiz_result(self, user_id, score, total_questions, accuracy,
                          avg_response_time, highest_streak, difficulty,
                          time_taken, mode="Quiz", question_log=None):
        """Persist a completed quiz/practice session and its per-question
        breakdown. Returns the new QuizHistory id."""
        cur = self.conn.cursor()
        now = datetime.now().isoformat()

        cur.execute(
            """INSERT INTO Scores
               (user_id, score, total_questions, accuracy, avg_response_time,
                highest_streak, difficulty, date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, score, total_questions, accuracy, avg_response_time,
             highest_streak, difficulty, now),
        )

        cur.execute(
            """INSERT INTO QuizHistory
               (user_id, quiz_date, score, total_questions, time_taken, difficulty, mode)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, now, score, total_questions, time_taken, difficulty, mode),
        )
        quiz_history_id = cur.lastrowid

        if question_log:
            for q in question_log:
                cur.execute(
                    """INSERT INTO QuestionHistory
                       (quiz_history_id, shape_name, rotation_angle, direction,
                        correct, response_time)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (quiz_history_id, q["shape_name"], q["rotation_angle"],
                     q["direction"], int(q["correct"]), q["response_time"]),
                )

        self.conn.commit()
        return quiz_history_id

    def add_achievement(self, user_id, name, description=""):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id FROM Achievements WHERE user_id = ? AND achievement_name = ?",
            (user_id, name),
        )
        if cur.fetchone():
            return False
        cur.execute(
            """INSERT INTO Achievements (user_id, achievement_name, description, date_earned)
               VALUES (?, ?, ?, ?)""",
            (user_id, name, description, datetime.now().isoformat()),
        )
        self.conn.commit()
        return True

    def get_achievements(self, user_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM Achievements WHERE user_id = ? ORDER BY date_earned DESC",
            (user_id,),
        )
        return [dict(r) for r in cur.fetchall()]

    # ------------------------------------------------------------------
    # Reads: previous scores / leaderboard / stats
    # ------------------------------------------------------------------
    def get_previous_scores(self, user_id, limit=50):
        cur = self.conn.cursor()
        cur.execute(
            """SELECT * FROM QuizHistory WHERE user_id = ?
               ORDER BY quiz_date DESC LIMIT ?""",
            (user_id, limit),
        )
        return [dict(r) for r in cur.fetchall()]

    def get_leaderboard_highest_score(self, limit=10):
        cur = self.conn.cursor()
        cur.execute(
            """SELECT Users.username, Scores.score, Scores.total_questions,
                      Scores.difficulty, Scores.date
               FROM Scores JOIN Users ON Scores.user_id = Users.id
               ORDER BY Scores.score DESC, Scores.date ASC LIMIT ?""",
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]

    def get_leaderboard_fastest(self, limit=10):
        cur = self.conn.cursor()
        cur.execute(
            """SELECT Users.username, QuizHistory.time_taken, QuizHistory.score,
                      QuizHistory.total_questions, QuizHistory.quiz_date
               FROM QuizHistory JOIN Users ON QuizHistory.user_id = Users.id
               WHERE QuizHistory.score = QuizHistory.total_questions
               ORDER BY QuizHistory.time_taken ASC LIMIT ?""",
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]

    def get_leaderboard_best_accuracy(self, limit=10):
        cur = self.conn.cursor()
        cur.execute(
            """SELECT Users.username, Scores.accuracy, Scores.total_questions,
                      Scores.difficulty, Scores.date
               FROM Scores JOIN Users ON Scores.user_id = Users.id
               ORDER BY Scores.accuracy DESC, Scores.total_questions DESC LIMIT ?""",
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]

    def get_statistics(self, user_id):
        cur = self.conn.cursor()
        cur.execute(
            """SELECT COUNT(*) as attempted,
                      SUM(correct) as correct_count,
                      AVG(response_time) as avg_time
               FROM QuestionHistory
               WHERE quiz_history_id IN
                     (SELECT id FROM QuizHistory WHERE user_id = ?)""",
            (user_id,),
        )
        overall = dict(cur.fetchone())

        cur.execute(
            """SELECT shape_name,
                      SUM(correct) as correct_count,
                      COUNT(*) as total
               FROM QuestionHistory
               WHERE quiz_history_id IN
                     (SELECT id FROM QuizHistory WHERE user_id = ?)
               GROUP BY shape_name""",
            (user_id,),
        )
        shape_rows = [dict(r) for r in cur.fetchall()]
        for row in shape_rows:
            row["accuracy"] = (row["correct_count"] / row["total"] * 100
                                if row["total"] else 0)
        shape_rows.sort(key=lambda r: r["accuracy"], reverse=True)
        strong = shape_rows[:3]
        weak = list(reversed(shape_rows[-3:])) if len(shape_rows) >= 3 else list(reversed(shape_rows))

        cur.execute(
            """SELECT DATE(quiz_date) as day, SUM(score) as day_score,
                      SUM(total_questions) as day_total
               FROM QuizHistory WHERE user_id = ?
               GROUP BY DATE(quiz_date) ORDER BY day ASC""",
            (user_id,),
        )
        daily_progress = [dict(r) for r in cur.fetchall()]

        attempted = overall["attempted"] or 0
        correct_count = overall["correct_count"] or 0
        accuracy = (correct_count / attempted * 100) if attempted else 0.0

        return {
            "questions_attempted": attempted,
            "accuracy": round(accuracy, 1),
            "strong_shapes": strong,
            "weak_shapes": weak,
            "avg_time_per_question": round(overall["avg_time"] or 0.0, 2),
            "daily_progress": daily_progress,
        }

    def close(self):
        self.conn.close()
