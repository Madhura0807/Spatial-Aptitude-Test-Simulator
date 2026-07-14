"""
app.py
Top-level application window. Owns shared state (database, sound manager,
settings, current user, active quiz controller) and switches between
screens using a simple stack-free frame-swapping router.
"""

import customtkinter as ctk

from src import config
from src.models.database import DatabaseManager
from src.utils import helpers
from src.utils.sound_manager import SoundManager


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.settings = helpers.load_settings()
        ctk.set_appearance_mode(self.settings.get("theme", "Dark"))
        ctk.set_default_color_theme("blue")

        self.title(config.APP_NAME)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        self.configure(fg_color=config.COLOR_BG_DARK)

        # ---------------- Shared application state ----------------
        self.db = DatabaseManager()
        self.current_user = self.db.get_or_create_user("Guest")
        self.sound = SoundManager(enabled=self.settings.get("sound_enabled", True))
        self.quiz_controller = None  # set when a Quiz/Practice session starts
        self.last_result_summary = None
        self.last_last_screen = None  # for Learn/Settings "back" navigation

        # ---------------- Frame container ----------------
        self.container = ctk.CTkFrame(self, fg_color=config.COLOR_BG_DARK, corner_radius=0)
        self.container.pack(fill="both", expand=True)

        self._current_frame = None
        self._current_frame_name = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Local import to avoid circular imports at module load time.
        from src.ui.splash_screen import SplashScreen
        from src.ui.home_screen import HomeScreen
        from src.ui.instructions_screen import InstructionsScreen
        from src.ui.quiz_screen import QuizScreen
        from src.ui.practice_screen import PracticeScreen
        from src.ui.learn_screen import LearnScreen
        from src.ui.result_screen import ResultScreen
        from src.ui.leaderboard_screen import LeaderboardScreen
        from src.ui.previous_scores_screen import PreviousScoresScreen
        from src.ui.settings_screen import SettingsScreen

        self.screen_registry = {
            "splash": SplashScreen,
            "home": HomeScreen,
            "instructions": InstructionsScreen,
            "quiz": QuizScreen,
            "practice": PracticeScreen,
            "learn": LearnScreen,
            "result": ResultScreen,
            "leaderboard": LeaderboardScreen,
            "previous_scores": PreviousScoresScreen,
            "settings": SettingsScreen,
        }

        self.show_frame("splash")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def show_frame(self, name, **kwargs):
        screen_cls = self.screen_registry[name]

        if self._current_frame is not None:
            destroy_hook = getattr(self._current_frame, "on_destroy", None)
            if callable(destroy_hook):
                try:
                    destroy_hook()
                except Exception:
                    pass
            self._current_frame.destroy()

        new_frame = screen_cls(self.container, self, **kwargs)
        new_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._current_frame = new_frame
        self._current_frame_name = name

        show_hook = getattr(new_frame, "on_show", None)
        if callable(show_hook):
            try:
                show_hook()
            except Exception:
                pass

    def current_screen_name(self):
        return self._current_frame_name

    # ------------------------------------------------------------------
    # Settings persistence
    # ------------------------------------------------------------------
    def update_setting(self, key, value):
        self.settings[key] = value
        helpers.save_settings(self.settings)
        if key == "sound_enabled":
            self.sound.set_enabled(value)
        if key == "theme":
            ctk.set_appearance_mode(value)

    def on_close(self):
        try:
            self.db.close()
        except Exception:
            pass
        self.destroy()
