"""
result_screen.py
Post-quiz Result screen: shows final score, accuracy, average response
time, and highest streak, plus a small confetti-style celebration
animation for a perfect score. Offers Retry / Home / Leaderboard actions.
"""

import random

import customtkinter as ctk

from src import config
from src.ui.widgets import AnimatedBackground, GlassCard, GradientButton


class ResultScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=config.COLOR_BG_DARK)
        self.app = app
        summary = app.last_result_summary or {
            "score": 0, "total_questions": 0, "accuracy": 0.0,
            "avg_response_time": 0.0, "highest_streak": 0, "difficulty": "Medium",
            "time_taken": 0.0,
        }

        self.background = AnimatedBackground(self, config.WINDOW_WIDTH, config.WINDOW_HEIGHT, num_shapes=10)
        self.background.place(relx=0, rely=0, relwidth=1, relheight=1)

        is_perfect = (summary["total_questions"] > 0 and
                      summary["score"] == summary["total_questions"])

        heading = "Perfect Score!" if is_perfect else "Quiz Complete!"
        ctk.CTkLabel(self, text=heading, font=config.FONT_TITLE,
                     text_color=config.COLOR_TEXT_PRIMARY).place(relx=0.5, rely=0.12, anchor="center")

        card = GlassCard(self, width=560, height=440)
        card.place(relx=0.5, rely=0.56, anchor="center")

        rows = [
            ("Final Score", f"{summary['score']} / {summary['total_questions']}"),
            ("Accuracy", f"{summary['accuracy']}%"),
            ("Average Response Time", f"{summary['avg_response_time']}s"),
            ("Highest Streak", f"{summary['highest_streak']}"),
            ("Difficulty", summary["difficulty"]),
            ("Total Time Taken", f"{summary['time_taken']}s"),
        ]
        for i, (label, value) in enumerate(rows):
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=40, pady=10)
            ctk.CTkLabel(row, text=label, font=config.FONT_BODY,
                         text_color=config.COLOR_TEXT_SECONDARY).pack(side="left")
            ctk.CTkLabel(row, text=value, font=config.FONT_SUBHEADING,
                         text_color=config.COLOR_TEXT_PRIMARY).pack(side="right")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.place(relx=0.5, rely=0.90, anchor="center")
        GradientButton(btn_frame, "Retry", primary=True, width=160,
                        command=lambda: app.show_frame("instructions")).grid(row=0, column=0, padx=10)
        GradientButton(btn_frame, "Home", primary=False, width=160,
                        command=lambda: app.show_frame("home")).grid(row=0, column=1, padx=10)
        GradientButton(btn_frame, "Leaderboard", primary=False, width=160,
                        command=lambda: app.show_frame("leaderboard")).grid(row=0, column=2, padx=10)

        self._confetti_items = []
        if is_perfect:
            self._run_confetti()

    def _run_confetti(self):
        colors = [config.COLOR_ACCENT_BLUE, config.COLOR_ACCENT_PURPLE,
                  config.COLOR_SUCCESS, config.COLOR_WARNING]
        pieces = []
        for _ in range(60):
            x = random.uniform(0, config.WINDOW_WIDTH)
            y = random.uniform(-200, 0)
            size = random.uniform(4, 9)
            speed = random.uniform(2.5, 5.5)
            drift = random.uniform(-1.2, 1.2)
            color = random.choice(colors)
            item = self.background.create_rectangle(x, y, x + size, y + size,
                                                      fill=color, outline="")
            pieces.append({"id": item, "x": x, "y": y, "speed": speed, "drift": drift})
        self._confetti_pieces = pieces
        self._confetti_tick()

    def _confetti_tick(self):
        if not getattr(self, "_confetti_pieces", None):
            return
        alive = False
        for piece in self._confetti_pieces:
            piece["y"] += piece["speed"]
            piece["x"] += piece["drift"]
            self.background.coords(piece["id"], piece["x"], piece["y"],
                                    piece["x"] + 6, piece["y"] + 6)
            if piece["y"] < config.WINDOW_HEIGHT + 20:
                alive = True
        if alive:
            try:
                self.after(30, self._confetti_tick)
            except Exception:
                pass

    def on_destroy(self):
        self.background.stop()
