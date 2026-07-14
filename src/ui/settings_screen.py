"""
settings_screen.py
Settings screen: theme (Dark/Light), default difficulty, timer duration,
default number of questions, and sound effects toggle. Persisted to a
local JSON file via src.utils.helpers.
"""

import customtkinter as ctk

from src import config
from src.ui.widgets import GlassCard, GradientButton, SectionLabel


class SettingsScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=config.COLOR_BG_DARK)
        self.app = app

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=(18, 4))
        ctk.CTkLabel(top_bar, text="Settings", font=config.FONT_HEADING,
                     text_color=config.COLOR_TEXT_PRIMARY).pack(side="left")
        GradientButton(top_bar, "Back to Home", primary=False, width=160,
                        command=lambda: app.show_frame("home")).pack(side="right")

        card = GlassCard(self, width=560, height=500)
        card.place(relx=0.5, rely=0.55, anchor="center")

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(padx=30, pady=30, fill="both", expand=True)

        row = 0
        SectionLabel(grid, "Theme").grid(row=row, column=0, sticky="w", pady=14)
        self.theme_var = ctk.StringVar(value=app.settings.get("theme", "Dark"))
        ctk.CTkSegmentedButton(grid, values=["Dark", "Light"], variable=self.theme_var,
                                selected_color=config.COLOR_ACCENT_BLUE,
                                command=self._on_theme_change).grid(row=row, column=1, pady=14, sticky="e")

        row += 1
        SectionLabel(grid, "Default Difficulty").grid(row=row, column=0, sticky="w", pady=14)
        self.difficulty_var = ctk.StringVar(value=app.settings.get("difficulty", config.DEFAULT_DIFFICULTY))
        ctk.CTkOptionMenu(grid, values=list(config.DIFFICULTY_PRESETS.keys()),
                           variable=self.difficulty_var, width=180,
                           fg_color=config.COLOR_SURFACE, button_color=config.COLOR_ACCENT_BLUE,
                           command=lambda v: app.update_setting("difficulty", v)
                           ).grid(row=row, column=1, pady=14, sticky="e")

        row += 1
        SectionLabel(grid, "Timer Duration (seconds)").grid(row=row, column=0, sticky="w", pady=14)
        self.timer_var = ctk.StringVar(value=str(app.settings.get("timer_seconds", config.DEFAULT_TIMER_SECONDS)))
        ctk.CTkOptionMenu(grid, values=["15", "20", "25", "30", "40", "60"],
                           variable=self.timer_var, width=180,
                           fg_color=config.COLOR_SURFACE, button_color=config.COLOR_ACCENT_BLUE,
                           command=lambda v: app.update_setting("timer_seconds", int(v))
                           ).grid(row=row, column=1, pady=14, sticky="e")

        row += 1
        SectionLabel(grid, "Number of Questions").grid(row=row, column=0, sticky="w", pady=14)
        self.num_q_var = ctk.StringVar(value=str(app.settings.get("num_questions", config.DEFAULT_NUM_QUESTIONS)))
        ctk.CTkOptionMenu(grid, values=["5", "10", "15", "20"],
                           variable=self.num_q_var, width=180,
                           fg_color=config.COLOR_SURFACE, button_color=config.COLOR_ACCENT_BLUE,
                           command=lambda v: app.update_setting("num_questions", int(v))
                           ).grid(row=row, column=1, pady=14, sticky="e")

        row += 1
        SectionLabel(grid, "Sound Effects").grid(row=row, column=0, sticky="w", pady=14)
        self.sound_var = ctk.BooleanVar(value=app.settings.get("sound_enabled", True))
        ctk.CTkSwitch(grid, text="", variable=self.sound_var, progress_color=config.COLOR_ACCENT_BLUE,
                       command=self._on_sound_toggle).grid(row=row, column=1, pady=14, sticky="e")

        row += 1
        self.status_label = ctk.CTkLabel(grid, text="", font=config.FONT_SMALL,
                                          text_color=config.COLOR_SUCCESS)
        self.status_label.grid(row=row, column=0, columnspan=2, pady=(20, 0))

        for c in (0, 1):
            grid.grid_columnconfigure(c, weight=1)

    def _on_theme_change(self, value):
        self.app.update_setting("theme", value)
        self._flash_saved()

    def _on_sound_toggle(self):
        enabled = self.sound_var.get()
        self.app.update_setting("sound_enabled", enabled)
        if enabled:
            self.app.sound.play_click()
        self._flash_saved()

    def _flash_saved(self):
        self.status_label.configure(text="Settings saved.")
        self.after(1500, lambda: self.status_label.configure(text=""))
