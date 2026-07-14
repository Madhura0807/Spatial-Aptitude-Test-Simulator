"""
practice_screen.py
Practice Mode: unlimited randomly generated questions with no timer
pressure. After each answer, the correct rotation is animated and a plain
-English explanation of why it is correct is shown.
"""

import customtkinter as ctk

from src import config
from src.controllers.quiz_controller import QuizController
from src.turtle_engine.canvas_manager import create_turtle_canvas, destroy_turtle_canvas
from src.turtle_engine.shapes import create_shape
from src.ui.widgets import GlassCard, GradientButton

MAIN_CANVAS_SIZE = 280
OPTION_CANVAS_SIZE = 120
OPTION_LETTERS = ["A", "B", "C", "D"]


class PracticeScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=config.COLOR_BG_DARK)
        self.app = app

        difficulty = app.settings.get("difficulty", config.DEFAULT_DIFFICULTY)
        self.controller = QuizController(
            db_manager=app.db, user_id=app.current_user["id"],
            difficulty=difficulty, num_questions=0, mode="Practice",
        )
        self._answered = False
        self.selected_index = None
        self._build_layout()
        self._load_question()

    def _build_layout(self):
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=(18, 4))
        ctk.CTkLabel(top_bar, text="Practice Mode", font=config.FONT_HEADING,
                     text_color=config.COLOR_TEXT_PRIMARY).pack(side="left")
        self.score_label = ctk.CTkLabel(top_bar, text="Correct: 0 / 0", font=config.FONT_SUBHEADING,
                                         text_color=config.COLOR_SUCCESS)
        self.score_label.pack(side="right")

        self.prompt_label = ctk.CTkLabel(self, text="", font=config.FONT_HEADING,
                                          text_color=config.COLOR_ACCENT_PURPLE)
        self.prompt_label.pack(pady=(6, 10))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack()

        main_card = GlassCard(body, width=MAIN_CANVAS_SIZE + 40, height=MAIN_CANVAS_SIZE + 40)
        main_card.grid(row=0, column=0, padx=20)
        main_card.pack_propagate(False)
        self.main_canvas, self.main_screen, self.main_turtle = create_turtle_canvas(
            main_card, MAIN_CANVAS_SIZE, MAIN_CANVAS_SIZE, bg_color=config.COLOR_GLASS,
        )
        self.main_canvas.pack(expand=True)

        self.explanation_card = GlassCard(body, width=340, height=MAIN_CANVAS_SIZE + 40)
        self.explanation_card.grid(row=0, column=1, padx=20)
        self.explanation_card.pack_propagate(False)
        ctk.CTkLabel(self.explanation_card, text="Explanation", font=config.FONT_SUBHEADING,
                     text_color=config.COLOR_TEXT_SECONDARY).pack(pady=(16, 6))
        self.explanation_label = ctk.CTkLabel(
            self.explanation_card, text="Select an option and submit to see the explanation here.",
            font=config.FONT_BODY, text_color=config.COLOR_TEXT_PRIMARY, wraplength=300, justify="left")
        self.explanation_label.pack(padx=16)

        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.pack(pady=16)

        self.option_cards = []
        self.option_canvases = []
        self.option_turtles = []

        for i in range(4):
            card = GlassCard(options_frame, width=OPTION_CANVAS_SIZE + 30,
                              height=OPTION_CANVAS_SIZE + 55, corner_radius=14)
            card.grid(row=0, column=i, padx=12)
            card.pack_propagate(False)
            letter = ctk.CTkLabel(card, text=OPTION_LETTERS[i], font=config.FONT_SUBHEADING,
                                   text_color=config.COLOR_TEXT_SECONDARY)
            letter.pack(pady=(6, 0))
            canvas, screen, t = create_turtle_canvas(
                card, OPTION_CANVAS_SIZE, OPTION_CANVAS_SIZE, bg_color=config.COLOR_SURFACE)
            canvas.pack(pady=4)
            for widget in (card, letter, canvas):
                widget.bind("<Button-1>", lambda e, idx=i: self._select_option(idx))
            self.option_cards.append(card)
            self.option_canvases.append((canvas, screen))
            self.option_turtles.append(t)

        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(pady=(4, 10))
        self.submit_btn = GradientButton(nav_frame, "Submit", primary=True, width=160,
                                          command=self._on_submit)
        self.submit_btn.grid(row=0, column=0, padx=10)
        self.next_btn = GradientButton(nav_frame, "Next Question", primary=True, width=180,
                                        command=self._on_next)
        self.next_btn.grid(row=0, column=1, padx=10)
        GradientButton(nav_frame, "Back to Home", primary=False, width=160,
                        command=lambda: self.app.show_frame("home")).grid(row=0, column=2, padx=10)

    def _load_question(self):
        question = self.controller.current_question()
        self._answered = False
        self.selected_index = None
        self.prompt_label.configure(text=question.prompt_text)
        self.explanation_label.configure(text="Select an option and submit to see the explanation here.")

        shape_kwargs = {"seed": question.shape_seed} if question.shape_name == "IrregularPolygon" else {}
        self.main_shape = create_shape(
            question.shape_name, self.main_turtle, size=90,
            color=config.COLOR_SHAPE_FILL, outline_color=config.COLOR_SHAPE_OUTLINE, **shape_kwargs)
        self.main_shape.draw()

        for i, option in enumerate(question.options):
            t = self.option_turtles[i]
            opt_shape_kwargs = {"seed": question.shape_seed} if question.shape_name == "IrregularPolygon" else {}
            shape = create_shape(
                question.shape_name, t, size=38,
                color=config.COLOR_SHAPE_FILL_ALT, outline_color=config.COLOR_SHAPE_OUTLINE, **opt_shape_kwargs)
            angle = option["angle"] if option["direction"] == "Clockwise" else -option["angle"]
            shape.draw(angle=angle % 360, mirrored=option["mirrored"])
            self.option_cards[i].configure(border_color=config.COLOR_GLASS_BORDER, border_width=1)

        self.controller.start_question_timer()
        self.submit_btn.configure(state="normal")
        self.next_btn.configure(state="disabled")

    def _select_option(self, idx):
        if self._answered:
            return
        self.app.sound.play_click()
        self.selected_index = idx
        for i, card in enumerate(self.option_cards):
            card.configure(
                border_color=config.COLOR_ACCENT_BLUE if i == idx else config.COLOR_GLASS_BORDER,
                border_width=3 if i == idx else 1)

    def _on_submit(self):
        if self._answered or self.selected_index is None:
            return
        question = self.controller.current_question()
        result = self.controller.submit_answer(self.selected_index)
        self._answered = True

        total = len(self.controller.question_log)
        self.score_label.configure(text=f"Correct: {self.controller.score} / {total}")

        for i, card in enumerate(self.option_cards):
            if i == question.correct_index:
                card.configure(border_color=config.COLOR_OPTION_CORRECT, border_width=3)
            elif i == self.selected_index:
                card.configure(border_color=config.COLOR_OPTION_WRONG, border_width=3)

        if result["correct"]:
            self.app.sound.play_correct()
        else:
            self.app.sound.play_wrong()

        angle = question.rotation_angle if question.direction == "Clockwise" else -question.rotation_angle
        self.main_shape.animate_rotation(angle, steps=20, delay_ms=18)

        self.explanation_label.configure(text=self._build_explanation(question, result["correct"]))
        self.submit_btn.configure(state="disabled")
        self.next_btn.configure(state="normal")

    def _build_explanation(self, question, was_correct):
        verdict = "Correct!" if was_correct else "Not quite."
        return (
            f"{verdict} Rotating a {question.shape_name} by {question.rotation_angle}\u00b0 "
            f"{question.direction} moves every vertex around the shape's center by that "
            f"exact angle while keeping its size and edge lengths unchanged. Option "
            f"{OPTION_LETTERS[question.correct_index]} shows this correctly. Watch the main "
            f"figure animate into the correct orientation above."
        )

    def _on_next(self):
        self.app.sound.play_click()
        self.controller.advance()
        self._load_question()

    def on_destroy(self):
        destroy_turtle_canvas(self.main_canvas, self.main_screen)
        for canvas, screen in self.option_canvases:
            destroy_turtle_canvas(canvas, screen)
