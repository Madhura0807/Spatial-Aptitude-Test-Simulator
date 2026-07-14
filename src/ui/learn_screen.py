"""
learn_screen.py
Learn Mode: browse every supported shape, see it drawn live by Turtle,
inspect its geometric properties (sides, vertices, symmetry, angles) and
real-life examples, and trigger a full 360 degree rotation demo animation.
"""

import customtkinter as ctk

from src import config
from src.turtle_engine.canvas_manager import create_turtle_canvas, destroy_turtle_canvas
from src.turtle_engine.shapes import SHAPE_REGISTRY, create_shape
from src.ui.widgets import GlassCard, GradientButton

CANVAS_SIZE = 300


class LearnScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=config.COLOR_BG_DARK)
        self.app = app
        self.shape_names = list(SHAPE_REGISTRY.keys())

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=(18, 4))
        ctk.CTkLabel(top_bar, text="Learn Shapes", font=config.FONT_HEADING,
                     text_color=config.COLOR_TEXT_PRIMARY).pack(side="left")
        GradientButton(top_bar, "Back to Home", primary=False, width=160,
                        command=lambda: app.show_frame("home")).pack(side="right")

        selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        selector_frame.pack(pady=(6, 10))
        ctk.CTkLabel(selector_frame, text="Choose a shape:", font=config.FONT_BODY,
                     text_color=config.COLOR_TEXT_SECONDARY).pack(side="left", padx=(0, 10))
        self.shape_var = ctk.StringVar(value=self.shape_names[0])
        self.shape_menu = ctk.CTkOptionMenu(
            selector_frame, values=[self._pretty(n) for n in self.shape_names],
            command=self._on_shape_selected, width=220,
            fg_color=config.COLOR_SURFACE, button_color=config.COLOR_ACCENT_BLUE)
        self.shape_menu.pack(side="left")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(pady=10)

        canvas_card = GlassCard(body, width=CANVAS_SIZE + 40, height=CANVAS_SIZE + 100)
        canvas_card.grid(row=0, column=0, padx=20)
        canvas_card.pack_propagate(False)
        self.canvas, self.screen, self.turtle = create_turtle_canvas(
            canvas_card, CANVAS_SIZE, CANVAS_SIZE, bg_color=config.COLOR_GLASS)
        self.canvas.pack(pady=(16, 8))
        GradientButton(canvas_card, "Rotate Demo (360\u00b0)", primary=True, width=220,
                        command=self._rotate_demo).pack(pady=(0, 16))

        self.props_card = GlassCard(body, width=380, height=CANVAS_SIZE + 100)
        self.props_card.grid(row=0, column=1, padx=20)
        self.props_card.pack_propagate(False)
        self.props_title = ctk.CTkLabel(self.props_card, text="", font=config.FONT_SUBHEADING,
                                         text_color=config.COLOR_ACCENT_PURPLE)
        self.props_title.pack(pady=(18, 10), padx=20, anchor="w")
        self.props_body = ctk.CTkLabel(self.props_card, text="", font=config.FONT_BODY,
                                        text_color=config.COLOR_TEXT_PRIMARY, justify="left",
                                        wraplength=340)
        self.props_body.pack(padx=20, anchor="w")
        self.examples_body = ctk.CTkLabel(self.props_card, text="", font=config.FONT_BODY,
                                           text_color=config.COLOR_TEXT_SECONDARY, justify="left",
                                           wraplength=340)
        self.examples_body.pack(padx=20, pady=(14, 0), anchor="w")

        self._load_shape(self.shape_names[0])

    def _pretty(self, name):
        out = []
        for ch in name:
            if ch.isupper() and out:
                out.append(" ")
            out.append(ch)
        return "".join(out)

    def _on_shape_selected(self, pretty_name):
        name = pretty_name.replace(" ", "")
        self._load_shape(name)

    def _load_shape(self, name):
        self.app.sound.play_click()
        self.current_shape = create_shape(
            name, self.turtle, size=100, color=config.COLOR_SHAPE_FILL,
            outline_color=config.COLOR_SHAPE_OUTLINE)
        self.current_shape.draw()

        props = self.current_shape.get_properties()
        self.props_title.configure(text=props["name"])

        def fmt(val):
            if val is None:
                return "N/A"
            if val == float("inf"):
                return "Infinite"
            return str(val)

        body_text = (
            f"Sides:  {fmt(props['sides'])}\n"
            f"Vertices:  {fmt(props['vertices'])}\n"
            f"Lines of Symmetry:  {fmt(props['lines_of_symmetry'])}\n"
            f"Rotational Symmetry Order:  {fmt(props['rotational_symmetry_order'])}\n"
            f"Interior Angle:  {fmt(props['interior_angle'])}\u00b0\n"
            f"Exterior Angle:  {fmt(props['exterior_angle'])}\u00b0"
        )
        self.props_body.configure(text=body_text)

        examples = ", ".join(props["real_life_examples"]) if props["real_life_examples"] else "N/A"
        self.examples_body.configure(text=f"Real-life examples:\n{examples}")

    def _rotate_demo(self):
        self.app.sound.play_click()
        self.current_shape.reset_position()
        self.current_shape.animate_rotation(360, steps=60, delay_ms=16)

    def on_destroy(self):
        destroy_turtle_canvas(self.canvas, self.screen)
