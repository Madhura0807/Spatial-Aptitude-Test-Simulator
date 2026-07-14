"""
helpers.py
Small stateless utility functions shared across the codebase: settings
load/save (JSON) and misc formatting helpers.
"""

import json
import os

from src import config


def load_settings():
    if not os.path.exists(config.SETTINGS_PATH):
        return dict(config.DEFAULT_SETTINGS)
    try:
        with open(config.SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(config.DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(config.DEFAULT_SETTINGS)


def save_settings(settings):
    os.makedirs(os.path.dirname(config.SETTINGS_PATH), exist_ok=True)
    with open(config.SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def format_seconds(seconds):
    seconds = max(0, int(round(seconds)))
    minutes, secs = divmod(seconds, 60)
    return f"{minutes:02d}:{secs:02d}"


def format_time_taken(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.1f}s"


def clamp(value, low, high):
    return max(low, min(high, value))
