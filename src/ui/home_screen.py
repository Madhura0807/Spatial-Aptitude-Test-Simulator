"""
home_screen.py
Home Dashboard: app title, animated background, and the primary
navigation buttons (Start Quiz, Practice Mode, Learn Shapes, Previous
Scores, Leaderboard, Settings, Exit).
"""

import customtkinter as ctk

from src import config
from src.ui.widgets import AnimatedBackground, GlassCard, GradientButton


class HomeScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=config.COLOR_BG_DARK)
        self.app = app

        self.background = AnimatedBackground(self, config.WINDOW_WIDTH, config.WINDOW_HEIGHT, num_shapes=12)
        self.background.place(relx=0, rely=0, relwidth=1, relheight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.place(relx=0.5, rely=0.10, anchor="center")
        ctk.CTkLabel(header, text=config.APP_NAME, font=config.FONT_TITLE,
                     text_color=config.COLOR_TEXT_PRIMARY).pack()
        ctk.CTkLabel(header, text=f"Welcome back, {app.current_user['username']}!",
                     font=config.FONT_BODY, text_color=config.COLOR_TEXT_SECONDARY).pack(pady=(4, 0))

        card = GlassCard(self, width=760, height=460)
        card.place(relx=0.5, rely=0.58, anchor="center")
        card.grid_propagate(False)

        buttons = [
            ("Start Quiz", lambda: app.show_frame("instructions"), True),
            ("Practice Mode", lambda: app.show_frame("practice"), True),
            ("Learn Shapes", lambda: app.show_frame("learn"), False),
            ("Previous Scores", lambda: app.show_frame("previous_scores"), False),
            ("Leaderboard", lambda: app.show_frame("leaderboard"), False),
            ("Settings", lambda: app.show_frame("settings"), False),
            ("Exit", app.on_close, False),
        ]

        for i in range(3):
            card.grid_columnconfigure(i, weight=1, uniform="col")

        for idx, (label, cmd, primary) in enumerate(buttons):
            row, col = divmod(idx, 3)
            btn = GradientButton(card, label, command=self._wrap(cmd), primary=primary,
                                  width=220, height=56)
            btn.grid(row=row, column=col, padx=20, pady=20, sticky="n")

    def _wrap(self, cmd):
        def _inner():
            self.app.sound.play_click()
            cmd()
        return _inner

    def on_destroy(self):
        self.background.stop()
