"""
splash_screen.py
Professional loading/splash screen: animated geometric background, a
Turtle-drawn rotating logo, and a progress bar that transitions to the
Home dashboard automatically (or immediately on click).
"""

import customtkinter as ctk

from src import config
from src.turtle_engine.canvas_manager import create_turtle_canvas, destroy_turtle_canvas
from src.turtle_engine.shapes import create_shape
from src.ui.widgets import AnimatedBackground, ProgressPill


class SplashScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=config.COLOR_BG_DARK)
        self.app = app
        self._advanced = False

        self.background = AnimatedBackground(self, config.WINDOW_WIDTH, config.WINDOW_HEIGHT, num_shapes=16)
        self.background.place(relx=0, rely=0, relwidth=1, relheight=1)

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        self.canvas, self.screen, self.turtle = create_turtle_canvas(
            center, 220, 220, bg_color=config.COLOR_BG_DARK
        )
        self.canvas.pack(pady=(0, 10))
        self.logo_shape = create_shape("Star", self.turtle, size=70,
                                        color=config.COLOR_ACCENT_PURPLE,
                                        outline_color=config.COLOR_ACCENT_BLUE)
        self.logo_shape.draw()

        title = ctk.CTkLabel(center, text=config.APP_NAME, font=config.FONT_TITLE,
                              text_color=config.COLOR_TEXT_PRIMARY)
        title.pack(pady=(0, 6))
        subtitle = ctk.CTkLabel(center, text="Sharpen your mental rotation skills",
                                 font=config.FONT_BODY, text_color=config.COLOR_TEXT_SECONDARY)
        subtitle.pack(pady=(0, 24))

        self.progress = ProgressPill(center, width=340)
        self.progress.set(0)
        self.progress.pack(pady=(0, 8))

        self.status_label = ctk.CTkLabel(center, text="Loading shapes engine...",
                                          font=config.FONT_SMALL, text_color=config.COLOR_TEXT_SECONDARY)
        self.status_label.pack()

        # CustomTkinter disallows bind_all (undefined behavior across all
        # widgets), so we bind the click-to-skip handler individually to
        # every widget that covers the visible screen area instead.
        for widget in (self, self.background, center, title, subtitle,
                       self.status_label, self.canvas):
            widget.bind("<Button-1>", self._skip)

        self._progress_value = 0.0
        self._spin_step()
        self._progress_step()

    def _spin_step(self):
        if self._advanced:
            return
        self.logo_shape.rotate(12)
        try:
            self.after(40, self._spin_step)
        except Exception:
            pass

    def _progress_step(self):
        if self._advanced:
            return
        self._progress_value = min(1.0, self._progress_value + 0.025)
        self.progress.set(self._progress_value)
        messages = [
            (0.2, "Loading shapes engine..."),
            (0.5, "Preparing rotation engine..."),
            (0.8, "Warming up the dashboard..."),
            (0.99, "Almost ready..."),
        ]
        for threshold, msg in messages:
            if self._progress_value <= threshold:
                self.status_label.configure(text=msg)
                break
        if self._progress_value >= 1.0:
            self._go_home()
        else:
            self.after(45, self._progress_step)

    def _skip(self, event=None):
        self._go_home()

    def _go_home(self):
        if self._advanced:
            return
        self._advanced = True
        self.app.show_frame("home")

    def on_destroy(self):
        self._advanced = True
        self.background.stop()
        destroy_turtle_canvas(self.canvas, self.screen)
