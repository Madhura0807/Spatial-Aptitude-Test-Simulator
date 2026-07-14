"""
config.py
Central configuration for the Spatial Aptitude Test Simulator.
Holds UI theme constants, difficulty presets, and application-wide settings.
No hardcoded values should appear anywhere else in the codebase -- everything
tunable lives here.
"""

import os

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "spatial_aptitude.db")
SETTINGS_PATH = os.path.join(DATABASE_DIR, "settings.json")

# ----------------------------------------------------------------------
# Window
# ----------------------------------------------------------------------
APP_NAME = "Spatial Aptitude Test Simulator"
WINDOW_WIDTH = 1180
WINDOW_HEIGHT = 760
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 680

# ----------------------------------------------------------------------
# Color Palette (Dark mode, Blue & Purple gradient glassmorphism theme)
# ----------------------------------------------------------------------
COLOR_BG_DARK = "#0F1021"
COLOR_BG_DARKER = "#0A0B18"
COLOR_SURFACE = "#171a30"
COLOR_GLASS = "#1E2140"
COLOR_GLASS_BORDER = "#3A3F6E"
COLOR_ACCENT_BLUE = "#4F7CFF"
COLOR_ACCENT_PURPLE = "#9B5CFF"
COLOR_ACCENT_BLUE_HOVER = "#3D66E0"
COLOR_ACCENT_PURPLE_HOVER = "#8347E6"
COLOR_TEXT_PRIMARY = "#F2F3FA"
COLOR_TEXT_SECONDARY = "#9CA0C4"
COLOR_SUCCESS = "#3DDC97"
COLOR_ERROR = "#FF6B81"
COLOR_WARNING = "#FFC55C"
COLOR_SHAPE_FILL = "#4F7CFF"
COLOR_SHAPE_FILL_ALT = "#9B5CFF"
COLOR_SHAPE_OUTLINE = "#F2F3FA"
COLOR_OPTION_CORRECT = "#3DDC97"
COLOR_OPTION_WRONG = "#FF6B81"

FONT_FAMILY = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"

FONT_TITLE = (FONT_FAMILY, 34, "bold")
FONT_HEADING = (FONT_FAMILY, 22, "bold")
FONT_SUBHEADING = (FONT_FAMILY, 16, "bold")
FONT_BODY = (FONT_FAMILY, 14)
FONT_SMALL = (FONT_FAMILY, 12)
FONT_BUTTON = (FONT_FAMILY, 15, "bold")

# ----------------------------------------------------------------------
# Difficulty presets
# Each preset controls: shape pool complexity, timer seconds, rotation set,
# whether mirrored ("flipped") distractor options are included, and points
# multiplier.
# ----------------------------------------------------------------------
DIFFICULTY_PRESETS = {
    "Easy": {
        "shape_pool": ["Triangle", "Square", "Rectangle", "Circle", "Pentagon", "Arrow"],
        "angles": [90, 180, 270],
        "timer_seconds": 40,
        "use_mirrored_distractors": False,
        "points_multiplier": 1,
    },
    "Medium": {
        "shape_pool": ["Triangle", "Square", "Rectangle", "Pentagon", "Hexagon",
                        "Star", "Arrow", "LShape", "TShape", "PlusShape"],
        "angles": [90, 180, 270, 360],
        "timer_seconds": 30,
        "use_mirrored_distractors": True,
        "points_multiplier": 1.5,
    },
    "Hard": {
        "shape_pool": ["Hexagon", "Octagon", "Star", "LShape", "TShape",
                        "PlusShape", "FlagShape", "HouseShape", "ChairShape"],
        "angles": [90, 180, 270],
        "timer_seconds": 22,
        "use_mirrored_distractors": True,
        "points_multiplier": 2,
    },
    "Expert": {
        "shape_pool": ["FlagShape", "HouseShape", "ChairShape", "IrregularPolygon",
                        "LShape", "TShape", "Star", "Octagon"],
        "angles": [90, 180, 270],
        "timer_seconds": 15,
        "use_mirrored_distractors": True,
        "points_multiplier": 3,
    },
}

DEFAULT_DIFFICULTY = "Medium"
DEFAULT_NUM_QUESTIONS = 10
DEFAULT_TIMER_SECONDS = 30
DEFAULT_SOUND_ENABLED = True
DEFAULT_THEME = "Dark"

ROTATION_DIRECTIONS = ["Clockwise", "Anti-clockwise"]

ALL_SHAPES = [
    "Triangle", "Square", "Rectangle", "Circle", "Pentagon", "Hexagon",
    "Octagon", "Star", "Arrow", "LShape", "TShape", "PlusShape",
    "FlagShape", "HouseShape", "ChairShape", "IrregularPolygon",
]

DEFAULT_SETTINGS = {
    "theme": DEFAULT_THEME,
    "difficulty": DEFAULT_DIFFICULTY,
    "timer_seconds": DEFAULT_TIMER_SECONDS,
    "num_questions": DEFAULT_NUM_QUESTIONS,
    "sound_enabled": DEFAULT_SOUND_ENABLED,
}
