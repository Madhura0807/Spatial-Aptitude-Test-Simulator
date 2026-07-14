"""
base_shape.py
Abstract base class for every Turtle-drawn geometric figure used across the
Quiz, Practice and Learn screens. Concrete shapes only need to implement
`_generate_vertices()` (and optionally override the property helpers).

Every shape supports the mandatory operations required by the spec:
    draw()              -> render the shape at its current rotation angle
    rotate(degrees)      -> instantly rotate by `degrees` and redraw
    animate_rotation()   -> smoothly animate a rotation over time
    clear()              -> wipe the turtle's drawing
    reset_position()     -> reset rotation angle to 0 and redraw
"""

import math
from abc import ABC, abstractmethod


class Shape(ABC):
    """Base class for all rotate-able turtle shapes."""

    #: Human readable display name, overridden by subclasses.
    display_name = "Shape"
    #: Real life examples shown in Learn Mode, overridden by subclasses.
    real_life_examples = []

    def __init__(self, turtle_obj, size=100, color="#4F7CFF",
                 outline_color="#F2F3FA", center=(0, 0)):
        self.t = turtle_obj
        self.size = size
        self.color = color
        self.outline_color = outline_color
        self.center = center
        self.rotation_angle = 0
        self.mirrored = False
        self._configure_turtle()
        self.base_vertices = self._generate_vertices()

    # ------------------------------------------------------------------
    # Turtle setup
    # ------------------------------------------------------------------
    def _configure_turtle(self):
        self.t.hideturtle()
        self.t.speed(0)
        self.t.penup()
        self.t.width(3)
        try:
            self.t.getscreen().tracer(0, 0)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Abstract geometry
    # ------------------------------------------------------------------
    @abstractmethod
    def _generate_vertices(self):
        """Return a list of (x, y) tuples relative to the shape center at
        rotation angle 0. Subclasses must implement this."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------
    def _current_vertices(self, angle_deg=None, mirrored=None):
        angle_deg = self.rotation_angle if angle_deg is None else angle_deg
        mirrored = self.mirrored if mirrored is None else mirrored
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        cx, cy = self.center
        result = []
        for x, y in self.base_vertices:
            if mirrored:
                x = -x
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            result.append((cx + rx, cy + ry))
        return result

    # ------------------------------------------------------------------
    # Public drawing API (required by spec)
    # ------------------------------------------------------------------
    def draw(self, angle=None, mirrored=None, fill=True):
        """Render the polygon outline (and fill) at the given angle."""
        verts = self._current_vertices(angle, mirrored)
        self.t.clear()
        self.t.pencolor(self.outline_color)
        self.t.penup()
        self.t.goto(verts[0])
        self.t.pendown()
        if fill:
            self.t.fillcolor(self.color)
            self.t.begin_fill()
        for v in verts[1:]:
            self.t.goto(v)
        self.t.goto(verts[0])
        if fill:
            self.t.end_fill()
        self.t.penup()
        self._draw_orientation_marker(angle, mirrored)
        self._refresh()

    def _draw_orientation_marker(self, angle=None, mirrored=None):
        """A small marker dot near the 'first' vertex so users can visually
        track rotation direction, especially useful for symmetric shapes
        like Circle/Square where rotation is otherwise hard to perceive."""
        verts = self._current_vertices(angle, mirrored)
        mx = sum(v[0] for v in verts) / len(verts)
        my = sum(v[1] for v in verts) / len(verts)
        marker_x = verts[0][0] * 0.85 + mx * 0.15
        marker_y = verts[0][1] * 0.85 + my * 0.15
        self.t.penup()
        self.t.goto(marker_x, marker_y)
        self.t.dot(10, "#FFC55C")
        self.t.goto(self.center)

    def _refresh(self):
        try:
            self.t.getscreen().update()
        except Exception:
            pass

    def rotate(self, degrees):
        """Instantly rotate by `degrees` (positive = clockwise) and redraw."""
        self.rotation_angle = (self.rotation_angle + degrees) % 360
        self.draw()
        return self.rotation_angle

    def animate_rotation(self, degrees, steps=24, delay_ms=16, on_complete=None):
        """Smoothly animate a rotation of `degrees` (positive = clockwise)
        using the Tkinter/Turtle event loop via `ontimer` so the GUI stays
        responsive. Calls `on_complete()` when finished."""
        screen = self.t.getscreen()
        start_angle = self.rotation_angle
        step_size = degrees / float(steps)
        state = {"count": 0}

        def _step():
            state["count"] += 1
            current = start_angle + step_size * state["count"]
            self.draw(angle=current % 360)
            if state["count"] < steps:
                screen.ontimer(_step, delay_ms)
            else:
                self.rotation_angle = (start_angle + degrees) % 360
                self.draw()
                if on_complete:
                    on_complete()

        _step()

    def reset_position(self):
        self.rotation_angle = 0
        self.mirrored = False
        self.draw()

    def clear(self):
        self.t.clear()
        self._refresh()

    def set_mirrored(self, mirrored):
        self.mirrored = mirrored
        self.draw()

    # ------------------------------------------------------------------
    # Learn-mode geometric properties
    # ------------------------------------------------------------------
    def num_sides(self):
        return len(self.base_vertices)

    def num_vertices(self):
        return len(self.base_vertices)

    def lines_of_symmetry(self):
        return 0

    def rotational_symmetry_order(self):
        return 1

    def interior_angle(self):
        n = self.num_sides()
        if n < 3:
            return None
        return round((n - 2) * 180 / n, 1)

    def exterior_angle(self):
        interior = self.interior_angle()
        if interior is None:
            return None
        return round(180 - interior, 1)

    def get_properties(self):
        return {
            "name": self.display_name,
            "sides": self.num_sides(),
            "vertices": self.num_vertices(),
            "lines_of_symmetry": self.lines_of_symmetry(),
            "rotational_symmetry_order": self.rotational_symmetry_order(),
            "interior_angle": self.interior_angle(),
            "exterior_angle": self.exterior_angle(),
            "real_life_examples": self.real_life_examples,
        }
