#!/usr/bin/env python3
"""
main.py
Entry point for the Spatial Aptitude Test Simulator.

Run with:
    python main.py

Requires Python 3.10+ with tkinter available (standard on most desktop
Python installs; on some Linux distros install it separately, e.g.
`sudo apt install python3-tk`).
"""

import os
import sys

# Ensure the project root is on sys.path so `from src...` imports work
# regardless of the current working directory the script is launched from.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ui.app import App  # noqa: E402


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
