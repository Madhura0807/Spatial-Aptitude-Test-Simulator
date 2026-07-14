"""
canvas_manager.py
Helper utilities to embed Turtle drawing surfaces (RawTurtle + TurtleScreen)
inside Tkinter / CustomTkinter frames. This is what allows the Turtle
canvas to live inside a modern glassmorphism GUI instead of opening its
own separate window.
"""

import tkinter as tk
import turtle


def create_turtle_canvas(parent, width, height, bg_color="#171a30",
                          highlight_color=None, border_width=0):
    """Create a Tkinter Canvas embedded in `parent`, wrap it with a
    TurtleScreen, and return (canvas, screen, raw_turtle).

    The caller is responsible for placing/packing/gridding the returned
    canvas widget into the layout.
    """
    canvas = tk.Canvas(
        parent, width=width, height=height, bg=bg_color,
        highlightthickness=border_width,
        highlightbackground=highlight_color or bg_color,
        highlightcolor=highlight_color or bg_color,
        bd=0,
    )
    screen = turtle.TurtleScreen(canvas)
    screen.bgcolor(bg_color)
    screen.tracer(0, 0)
    raw_turtle = turtle.RawTurtle(screen)
    raw_turtle.hideturtle()
    raw_turtle.speed(0)
    raw_turtle.penup()
    return canvas, screen, raw_turtle


def destroy_turtle_canvas(canvas, screen):
    """Cleanly tear down a turtle canvas (call before destroying the
    parent frame to avoid orphaned `ontimer` callbacks)."""
    try:
        screen.clear()
    except Exception:
        pass
    try:
        canvas.destroy()
    except Exception:
        pass
