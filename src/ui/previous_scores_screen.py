"""
previous_scores_screen.py
Previous Scores / Statistics screen: a scrollable history of past
quiz/practice attempts plus aggregate stats (questions attempted, overall
accuracy, strongest/weakest shapes, average time per question) and any
earned achievement badges.
"""

import customtkinter as ctk

from src import config
from src.controllers.stats_controller import StatsController
from src.ui.widgets import GlassCard, GradientButton


class PreviousScoresScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=config.COLOR_BG_DARK)
        self.app = app
        self.stats = StatsController(app.db)
        user_id = app.current_user["id"]

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=(18, 4))
        ctk.CTkLabel(top_bar, text="Previous Scores & Statistics", font=config.FONT_HEADING,
                     text_color=config.COLOR_TEXT_PRIMARY).pack(side="left")
        GradientButton(top_bar, "Back to Home", primary=False, width=160,
                        command=lambda: app.show_frame("home")).pack(side="right")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=30, pady=10)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)

        # ---------------- Left: history list ----------------
        history_card = GlassCard(body, width=520, height=520)
        history_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        ctk.CTkLabel(history_card, text="Quiz History", font=config.FONT_SUBHEADING,
                     text_color=config.COLOR_TEXT_SECONDARY).pack(pady=(14, 6), padx=16, anchor="w")

        scroll = ctk.CTkScrollableFrame(history_card, width=480, height=440, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=6)

        history = self.stats.get_previous_scores(user_id)
        if not history:
            ctk.CTkLabel(scroll, text="No quiz attempts yet -- start a quiz to build your history!",
                         font=config.FONT_BODY, text_color=config.COLOR_TEXT_SECONDARY).pack(pady=30)
        else:
            for entry in history:
                self._history_row(scroll, entry)

        # ---------------- Right: aggregate stats ----------------
        stats_card = GlassCard(body, width=340, height=520)
        stats_card.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(stats_card, text="Overall Statistics", font=config.FONT_SUBHEADING,
                     text_color=config.COLOR_TEXT_SECONDARY).pack(pady=(14, 10), padx=16, anchor="w")

        overview = self.stats.get_user_statistics(user_id)
        rows = [
            ("Questions Attempted", overview["questions_attempted"]),
            ("Accuracy", f"{overview['accuracy']}%"),
            ("Avg. Time / Question", f"{overview['avg_time_per_question']}s"),
        ]
        for label, value in rows:
            row = ctk.CTkFrame(stats_card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=6)
            ctk.CTkLabel(row, text=label, font=config.FONT_BODY,
                         text_color=config.COLOR_TEXT_SECONDARY).pack(side="left")
            ctk.CTkLabel(row, text=str(value), font=config.FONT_SUBHEADING,
                         text_color=config.COLOR_TEXT_PRIMARY).pack(side="right")

        ctk.CTkLabel(stats_card, text="Strong Shapes", font=config.FONT_SMALL,
                     text_color=config.COLOR_SUCCESS).pack(pady=(16, 2), padx=18, anchor="w")
        strong_text = ", ".join(s["shape_name"] for s in overview["strong_shapes"]) or "N/A"
        ctk.CTkLabel(stats_card, text=strong_text, font=config.FONT_BODY, wraplength=300,
                     text_color=config.COLOR_TEXT_PRIMARY, justify="left").pack(padx=18, anchor="w")

        ctk.CTkLabel(stats_card, text="Weak Shapes", font=config.FONT_SMALL,
                     text_color=config.COLOR_ERROR).pack(pady=(14, 2), padx=18, anchor="w")
        weak_text = ", ".join(s["shape_name"] for s in overview["weak_shapes"]) or "N/A"
        ctk.CTkLabel(stats_card, text=weak_text, font=config.FONT_BODY, wraplength=300,
                     text_color=config.COLOR_TEXT_PRIMARY, justify="left").pack(padx=18, anchor="w")

        achievements = self.stats.get_achievements(user_id)
        ctk.CTkLabel(stats_card, text="Achievements", font=config.FONT_SMALL,
                     text_color=config.COLOR_WARNING).pack(pady=(14, 2), padx=18, anchor="w")
        if achievements:
            ach_text = "\n".join(f"\u2605 {a['achievement_name']}" for a in achievements[:5])
        else:
            ach_text = "None yet -- keep playing!"
        ctk.CTkLabel(stats_card, text=ach_text, font=config.FONT_BODY, wraplength=300,
                     text_color=config.COLOR_TEXT_PRIMARY, justify="left").pack(padx=18, anchor="w", pady=(0, 10))

    def _history_row(self, parent, entry):
        card = GlassCard(parent, height=64, corner_radius=12, fg_color=config.COLOR_SURFACE)
        card.pack(fill="x", pady=5)
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", padx=14, pady=8, fill="both", expand=True)
        date_str = entry["quiz_date"].split("T")[0] if "T" in entry["quiz_date"] else entry["quiz_date"]
        ctk.CTkLabel(left, text=f"{entry['mode']}  \u2022  {entry['difficulty']}",
                     font=config.FONT_BODY, text_color=config.COLOR_TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(left, text=date_str, font=config.FONT_SMALL,
                     text_color=config.COLOR_TEXT_SECONDARY).pack(anchor="w")

        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="right", padx=14)
        ctk.CTkLabel(right, text=f"{entry['score']} / {entry['total_questions']}",
                     font=config.FONT_SUBHEADING, text_color=config.COLOR_SUCCESS).pack(anchor="e")
        ctk.CTkLabel(right, text=f"{entry['time_taken']:.1f}s", font=config.FONT_SMALL,
                     text_color=config.COLOR_TEXT_SECONDARY).pack(anchor="e")
