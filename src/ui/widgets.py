"""
widgets.py
Reusable, professionally-styled CustomTkinter widgets shared by every
screen: glass cards, gradient buttons, and an animated geometric
background used on the Splash/Home screens for a modern feel.
"""

import math
import random
import tkinter as tk

import customtkinter as ctk

from src import config


class GlassCard(ctk.CTkFrame):
    """A frosted-glass styled card: rounded corners, subtle border, and a
    slightly lighter fill than the page background to fake a glassmorphism
    look (CustomTkinter has no real blur support)."""

    def __init__(self, parent, **kwargs):
        corner_radius = kwargs.pop("corner_radius", 18)
        fg_color = kwargs.pop("fg_color", config.COLOR_GLASS)
        border_width = kwargs.pop("border_width", 1)
        border_color = kwargs.pop("border_color", config.COLOR_GLASS_BORDER)
        super().__init__(
            parent, corner_radius=corner_radius, fg_color=fg_color,
            border_width=border_width, border_color=border_color, **kwargs
        )


class GradientButton(ctk.CTkButton):
    """A CTkButton pre-styled to look like a blue-to-purple gradient pill
    (CustomTkinter buttons are single-color, so we approximate the
    'gradient' with the accent purple and a matching hover shade)."""

    def __init__(self, parent, text, command=None, primary=True,
                 width=220, height=48, font=None, **kwargs):
        fg = config.COLOR_ACCENT_BLUE if primary else "transparent"
        hover = config.COLOR_ACCENT_BLUE_HOVER if primary else config.COLOR_GLASS
        border_width = 0 if primary else 2
        border_color = config.COLOR_ACCENT_PURPLE
        text_color = config.COLOR_TEXT_PRIMARY
        super().__init__(
            parent, text=text, command=command, width=width, height=height,
            corner_radius=height // 2, fg_color=fg, hover_color=hover,
            border_width=border_width, border_color=border_color,
            text_color=text_color, font=font or config.FONT_BUTTON,
            **kwargs
        )


class SectionLabel(ctk.CTkLabel):
    def __init__(self, parent, text, **kwargs):
        font = kwargs.pop("font", config.FONT_SUBHEADING)
        text_color = kwargs.pop("text_color", config.COLOR_TEXT_SECONDARY)
        super().__init__(parent, text=text, font=font, text_color=text_color, **kwargs)


class AnimatedBackground(tk.Canvas):
    """A subtle, continuously drifting field of translucent-looking blue
    and purple geometric shapes used behind the Splash and Home screens.
    Pure Tkinter canvas primitives (no Turtle) so it can sit *behind*
    other widgets cheaply."""

    SHAPE_COLORS = [config.COLOR_ACCENT_BLUE, config.COLOR_ACCENT_PURPLE]

    def __init__(self, parent, width, height, num_shapes=14, **kwargs):
        super().__init__(parent, width=width, height=height,
                          bg=config.COLOR_BG_DARK, highlightthickness=0, **kwargs)
        self._width = width
        self._height = height
        self._shapes = []
        self._running = True
        for _ in range(num_shapes):
            self._spawn_shape()
        self._animate()

    def _spawn_shape(self):
        x = random.uniform(0, self._width)
        y = random.uniform(0, self._height)
        size = random.uniform(18, 60)
        dx = random.uniform(-0.35, 0.35)
        dy = random.uniform(-0.2, 0.2)
        color = random.choice(self.SHAPE_COLORS)
        sides = random.choice([3, 4, 6, 0])  # 0 = circle
        angle = random.uniform(0, 360)
        spin = random.uniform(-0.4, 0.4)
        item = self._draw_polygon(x, y, size, sides, angle, color)
        self._shapes.append({
            "id": item, "x": x, "y": y, "size": size, "dx": dx, "dy": dy,
            "sides": sides, "angle": angle, "spin": spin, "color": color,
        })

    def _draw_polygon(self, x, y, size, sides, angle, color):
        if sides == 0:
            return self.create_oval(x - size / 2, y - size / 2, x + size / 2, y + size / 2,
                                     outline=color, width=1.5)
        pts = []
        for i in range(sides):
            a = math.radians(angle + i * 360 / sides)
            pts.append(x + size * math.cos(a))
            pts.append(y + size * math.sin(a))
        return self.create_polygon(pts, outline=color, fill="", width=1.5)

    def _animate(self):
        if not self._running:
            return
        for shape in self._shapes:
            shape["x"] += shape["dx"]
            shape["y"] += shape["dy"]
            shape["angle"] += shape["spin"]
            if shape["x"] < -80 or shape["x"] > self._width + 80:
                shape["dx"] *= -1
            if shape["y"] < -80 or shape["y"] > self._height + 80:
                shape["dy"] *= -1
            self.delete(shape["id"])
            shape["id"] = self._draw_polygon(
                shape["x"], shape["y"], shape["size"], shape["sides"],
                shape["angle"], shape["color"]
            )
        try:
            self.after(40, self._animate)
        except tk.TclError:
            self._running = False

    def stop(self):
        self._running = False


class ProgressPill(ctk.CTkProgressBar):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent, progress_color=config.COLOR_ACCENT_PURPLE,
            fg_color=config.COLOR_SURFACE, corner_radius=8, height=14, **kwargs
        )
