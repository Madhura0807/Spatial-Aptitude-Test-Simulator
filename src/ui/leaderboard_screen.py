"""
leaderboard_screen.py
Leaderboard: three tabs (Highest Score, Fastest Completion, Best Accuracy)
each backed by a SQLite query via StatsController, rendered in a scrollable
list.
"""

import customtkinter as ctk

from src import config
from src.controllers.stats_controller import StatsController
from src.ui.widgets import GlassCard, GradientButton


class LeaderboardScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=config.COLOR_BG_DARK)
        self.app = app
        self.stats = StatsController(app.db)

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=(18, 4))
        ctk.CTkLabel(top_bar, text="Leaderboard", font=config.FONT_HEADING,
                     text_color=config.COLOR_TEXT_PRIMARY).pack(side="left")
        GradientButton(top_bar, "Back to Home", primary=False, width=160,
                        command=lambda: app.show_frame("home")).pack(side="right")

        self.tabview = ctk.CTkTabview(
            self, width=820, height=560, fg_color=config.COLOR_GLASS,
            segmented_button_selected_color=config.COLOR_ACCENT_BLUE,
            segmented_button_selected_hover_color=config.COLOR_ACCENT_BLUE_HOVER)
        self.tabview.pack(pady=16)

        self.tabview.add("Highest Score")
        self.tabview.add("Fastest Completion")
        self.tabview.add("Best Accuracy")

        data = self.stats.get_leaderboards()
        self._populate_score(self.tabview.tab("Highest Score"), data["highest_score"])
        self._populate_fastest(self.tabview.tab("Fastest Completion"), data["fastest_completion"])
        self._populate_accuracy(self.tabview.tab("Best Accuracy"), data["best_accuracy"])

    def _make_scroll(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, width=780, height=480,
                                         fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        return scroll

    def _header_row(self, parent, cols):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 6))
        for i, text in enumerate(cols):
            ctk.CTkLabel(row, text=text, font=config.FONT_SUBHEADING,
                         text_color=config.COLOR_TEXT_SECONDARY, width=180,
                         anchor="w").grid(row=0, column=i, padx=10)

    def _empty_state(self, parent, message):
        ctk.CTkLabel(parent, text=message, font=config.FONT_BODY,
                     text_color=config.COLOR_TEXT_SECONDARY).pack(pady=40)

    def _populate_score(self, parent, rows):
        scroll = self._make_scroll(parent)
        if not rows:
            self._empty_state(scroll, "No scores recorded yet -- take a quiz to appear here!")
            return
        self._header_row(scroll, ["#", "Player", "Score", "Difficulty"])
        for i, r in enumerate(rows, start=1):
            self._data_row(scroll, [
                str(i), r["username"], f"{r['score']} / {r['total_questions']}", r["difficulty"]
            ], highlight=(i == 1))

    def _populate_fastest(self, parent, rows):
        scroll = self._make_scroll(parent)
        if not rows:
            self._empty_state(scroll, "No perfect, timed runs recorded yet.")
            return
        self._header_row(scroll, ["#", "Player", "Time Taken", "Questions"])
        for i, r in enumerate(rows, start=1):
            self._data_row(scroll, [
                str(i), r["username"], f"{r['time_taken']:.1f}s", str(r["total_questions"])
            ], highlight=(i == 1))

    def _populate_accuracy(self, parent, rows):
        scroll = self._make_scroll(parent)
        if not rows:
            self._empty_state(scroll, "No accuracy data recorded yet.")
            return
        self._header_row(scroll, ["#", "Player", "Accuracy", "Difficulty"])
        for i, r in enumerate(rows, start=1):
            self._data_row(scroll, [
                str(i), r["username"], f"{r['accuracy']}%", r["difficulty"]
            ], highlight=(i == 1))

    def _data_row(self, parent, values, highlight=False):
        card = GlassCard(parent, height=48, corner_radius=10,
                          fg_color=config.COLOR_ACCENT_BLUE if highlight else config.COLOR_SURFACE)
        card.pack(fill="x", pady=4)
        for i, val in enumerate(values):
            ctk.CTkLabel(card, text=val, font=config.FONT_BODY,
                         text_color=config.COLOR_TEXT_PRIMARY, width=180,
                         anchor="w").grid(row=0, column=i, padx=10, pady=8)
