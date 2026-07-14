"""
instructions_screen.py
Pre-quiz instructions and configuration screen. Lets the user confirm the
difficulty, number of questions, and timer duration (defaulting to the
values from Settings) before starting the Quiz.
"""

import customtkinter as ctk

from src import config
from src.ui.widgets import GlassCard, GradientButton, SectionLabel


class InstructionsScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=config.COLOR_BG_DARK)
        self.app = app

        ctk.CTkLabel(self, text="Quiz Instructions", font=config.FONT_HEADING,
                     text_color=config.COLOR_TEXT_PRIMARY).place(relx=0.5, rely=0.08, anchor="center")

        card = GlassCard(self, width=760, height=520)
        card.place(relx=0.5, rely=0.55, anchor="center")

        rules = (
            "1.  Each question shows a shape and a required rotation, e.g. '90\u00b0 Clockwise'.\n"
            "2.  Study the original figure carefully in the central Turtle canvas.\n"
            "3.  Choose the option (A, B, C or D) that matches the figure AFTER "
            "the rotation is applied.\n"
            "4.  A countdown timer runs for every question -- if it reaches zero the "
            "question is marked unanswered.\n"
            "5.  You may move between questions with Previous / Next and submit at any time.\n"
            "6.  Your score, accuracy, streak and response time are tracked and saved "
            "to your profile."
        )
        ctk.CTkLabel(card, text=rules, font=config.FONT_BODY, justify="left",
                     text_color=config.COLOR_TEXT_PRIMARY, wraplength=680).pack(
            padx=30, pady=(30, 20), anchor="w")

        options_frame = ctk.CTkFrame(card, fg_color="transparent")
        options_frame.pack(pady=10, fill="x", padx=30)

        SectionLabel(options_frame, "Difficulty").grid(row=0, column=0, padx=10, pady=6, sticky="w")
        self.difficulty_var = ctk.StringVar(value=app.settings.get("difficulty", config.DEFAULT_DIFFICULTY))
        ctk.CTkOptionMenu(options_frame, values=list(config.DIFFICULTY_PRESETS.keys()),
                           variable=self.difficulty_var, width=180,
                           fg_color=config.COLOR_SURFACE,
                           button_color=config.COLOR_ACCENT_BLUE).grid(row=0, column=1, padx=10, pady=6)

        SectionLabel(options_frame, "Number of Questions").grid(row=1, column=0, padx=10, pady=6, sticky="w")
        self.num_questions_var = ctk.StringVar(value=str(app.settings.get("num_questions", config.DEFAULT_NUM_QUESTIONS)))
        ctk.CTkOptionMenu(options_frame, values=["5", "10", "15", "20"],
                           variable=self.num_questions_var, width=180,
                           fg_color=config.COLOR_SURFACE,
                           button_color=config.COLOR_ACCENT_BLUE).grid(row=1, column=1, padx=10, pady=6)

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=(24, 10))
        GradientButton(btn_frame, "Back to Home", primary=False,
                        command=lambda: app.show_frame("home")).grid(row=0, column=0, padx=12)
        GradientButton(btn_frame, "Begin Quiz", primary=True,
                        command=self._begin).grid(row=0, column=1, padx=12)

    def _begin(self):
        self.app.sound.play_click()
        difficulty = self.difficulty_var.get()
        num_questions = int(self.num_questions_var.get())
        self.app.show_frame("quiz", difficulty=difficulty, num_questions=num_questions)
