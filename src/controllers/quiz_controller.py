"""
quiz_controller.py
Orchestrates a single Quiz/Practice session: owns the question list,
current index, running score, streaks, per-question timings, and talks to
the DatabaseManager to persist results at the end of a session.
"""

import time

from src import config
from src.controllers.question_generator import QuestionGenerator


class QuizController:
    def __init__(self, db_manager, user_id, difficulty=config.DEFAULT_DIFFICULTY,
                 num_questions=config.DEFAULT_NUM_QUESTIONS, mode="Quiz"):
        self.db = db_manager
        self.user_id = user_id
        self.difficulty = difficulty
        self.num_questions = num_questions
        self.mode = mode  # "Quiz" | "Practice" | "Daily Challenge"

        self.generator = QuestionGenerator(difficulty)
        self.questions = (self.generator.generate_batch(num_questions)
                           if mode != "Practice" else [])

        self.current_index = 0
        self.score = 0
        self.current_streak = 0
        self.highest_streak = 0
        self.question_log = []  # list of dicts for DB + stats
        self.answers_given = {}  # index -> chosen_option_index
        self._question_start_time = None
        self._session_start_time = time.time()

    # ------------------------------------------------------------------
    # Question flow
    # ------------------------------------------------------------------
    def current_question(self):
        if self.mode == "Practice":
            if len(self.questions) <= self.current_index:
                self.questions.append(self.generator.generate_question())
        if self.current_index >= len(self.questions):
            return None
        return self.questions[self.current_index]

    def start_question_timer(self):
        self._question_start_time = time.time()

    def elapsed_on_current_question(self):
        if self._question_start_time is None:
            return 0.0
        return time.time() - self._question_start_time

    def submit_answer(self, chosen_index):
        """Record the answer for the current question. Returns a dict
        summarizing whether it was correct, for UI feedback."""
        question = self.current_question()
        response_time = self.elapsed_on_current_question()
        correct = (chosen_index == question.correct_index)

        self.answers_given[self.current_index] = chosen_index

        if correct:
            self.score += 1
            self.current_streak += 1
            self.highest_streak = max(self.highest_streak, self.current_streak)
        else:
            self.current_streak = 0

        self.question_log.append({
            "shape_name": question.shape_name,
            "rotation_angle": question.rotation_angle,
            "direction": question.direction,
            "correct": correct,
            "response_time": round(response_time, 2),
        })

        return {
            "correct": correct,
            "correct_index": question.correct_index,
            "response_time": round(response_time, 2),
            "streak": self.current_streak,
        }

    def has_next(self):
        if self.mode == "Practice":
            return True
        return self.current_index + 1 < len(self.questions)

    def advance(self):
        self.current_index += 1

    def has_previous(self):
        return self.current_index > 0

    def go_back(self):
        if self.has_previous():
            self.current_index -= 1

    def is_finished(self):
        if self.mode == "Practice":
            return False
        return self.current_index >= len(self.questions)

    # ------------------------------------------------------------------
    # Session summary / persistence
    # ------------------------------------------------------------------
    def accuracy(self):
        answered = len(self.question_log)
        if answered == 0:
            return 0.0
        correct = sum(1 for q in self.question_log if q["correct"])
        return round(correct / answered * 100, 1)

    def average_response_time(self):
        if not self.question_log:
            return 0.0
        return round(sum(q["response_time"] for q in self.question_log) / len(self.question_log), 2)

    def total_time_taken(self):
        return round(time.time() - self._session_start_time, 2)

    def finish_and_save(self):
        """Persist this session to the database and return the summary
        dict used to populate the Result screen."""
        total_questions = len(self.question_log) or self.num_questions
        summary = {
            "score": self.score,
            "total_questions": total_questions,
            "accuracy": self.accuracy(),
            "avg_response_time": self.average_response_time(),
            "highest_streak": self.highest_streak,
            "difficulty": self.difficulty,
            "time_taken": self.total_time_taken(),
        }
        self.db.save_quiz_result(
            user_id=self.user_id,
            score=summary["score"],
            total_questions=summary["total_questions"],
            accuracy=summary["accuracy"],
            avg_response_time=summary["avg_response_time"],
            highest_streak=summary["highest_streak"],
            difficulty=summary["difficulty"],
            time_taken=summary["time_taken"],
            mode=self.mode,
            question_log=self.question_log,
        )
        self._check_achievements(summary)
        return summary

    def _check_achievements(self, summary):
        if summary["score"] == summary["total_questions"] and summary["total_questions"] > 0:
            self.db.add_achievement(
                self.user_id, "Perfect Score",
                f"Answered all {summary['total_questions']} questions correctly."
            )
        if summary["highest_streak"] >= 5:
            self.db.add_achievement(
                self.user_id, "On Fire",
                f"Reached a streak of {summary['highest_streak']} correct answers in a row."
            )
        if self.difficulty == "Expert" and summary["accuracy"] >= 70:
            self.db.add_achievement(
                self.user_id, "Expert Navigator",
                "Scored 70%+ accuracy on Expert difficulty."
            )
