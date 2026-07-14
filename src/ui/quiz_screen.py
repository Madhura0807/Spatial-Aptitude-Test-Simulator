"""
quiz_screen.py
The core Quiz screen: shows the original shape on a central Turtle
canvas, the rotation prompt, a countdown timer, a progress bar, running
score, four Turtle-drawn answer options, and Previous / Next / Submit
controls. On submit, the correct rotation is animated live.
"""

import customtkinter as ctk

from src import config
from src.controllers.quiz_controller import QuizController
from src.turtle_engine.canvas_manager import create_turtle_canvas, destroy_turtle_canvas
from src.turtle_engine.shapes import create_shape
from src.ui.widgets import GlassCard, GradientButton, ProgressPill

MAIN_CANVAS_SIZE = 300
OPTION_CANVAS_SIZE = 130
OPTION_LETTERS = ["A", "B", "C", "D"]


class QuizScreen(ctk.CTkFrame):
    def __init__(self, parent, app, difficulty=None, num_questions=None):
        super().__init__(parent, fg_color=config.COLOR_BG_DARK)
        self.app = app

        difficulty = difficulty or app.settings.get("difficulty", config.DEFAULT_DIFFICULTY)
        num_questions = num_questions or app.settings.get("num_questions", config.DEFAULT_NUM_QUESTIONS)

        self.controller = QuizController(
            db_manager=app.db, user_id=app.current_user["id"],
            difficulty=difficulty, num_questions=num_questions, mode="Quiz",
        )
        app.quiz_controller = self.controller

        self.timer_seconds_total = self.controller.generator.preset["timer_seconds"]
        self._timer_remaining = self.timer_seconds_total
        self._timer_job = None
        self._answered_this_view = False
        self.selected_index = None

        self._build_layout()
        self._load_question()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_layout(self):
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=(18, 4))

        self.question_label = ctk.CTkLabel(top_bar, text="", font=config.FONT_SUBHEADING,
                                            text_color=config.COLOR_TEXT_PRIMARY)
        self.question_label.pack(side="left")

        self.score_label = ctk.CTkLabel(top_bar, text="Score: 0", font=config.FONT_SUBHEADING,
                                         text_color=config.COLOR_SUCCESS)
        self.score_label.pack(side="right", padx=(20, 0))

        self.timer_label = ctk.CTkLabel(top_bar, text="", font=config.FONT_SUBHEADING,
                                         text_color=config.COLOR_WARNING)
        self.timer_label.pack(side="right", padx=(20, 0))

        self.progress = ProgressPill(self, width=config.WINDOW_WIDTH - 100)
        self.progress.pack(pady=(4, 10))

        self.prompt_label = ctk.CTkLabel(self, text="", font=config.FONT_HEADING,
                                          text_color=config.COLOR_ACCENT_PURPLE)
        self.prompt_label.pack(pady=(2, 10))

        main_card = GlassCard(self, width=MAIN_CANVAS_SIZE + 40, height=MAIN_CANVAS_SIZE + 40)
        main_card.pack(pady=4)
        main_card.pack_propagate(False)
        self.main_canvas, self.main_screen, self.main_turtle = create_turtle_canvas(
            main_card, MAIN_CANVAS_SIZE, MAIN_CANVAS_SIZE, bg_color=config.COLOR_GLASS,
        )
        self.main_canvas.pack(expand=True)

        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.pack(pady=14)

        self.option_cards = []
        self.option_canvases = []
        self.option_turtles = []
        self.option_shapes = [None, None, None, None]

        for i in range(4):
            card = GlassCard(options_frame, width=OPTION_CANVAS_SIZE + 30,
                              height=OPTION_CANVAS_SIZE + 55, corner_radius=14)
            card.grid(row=0, column=i, padx=12)
            card.pack_propagate(False)

            letter = ctk.CTkLabel(card, text=OPTION_LETTERS[i], font=config.FONT_SUBHEADING,
                                   text_color=config.COLOR_TEXT_SECONDARY)
            letter.pack(pady=(6, 0))

            canvas, screen, t = create_turtle_canvas(
                card, OPTION_CANVAS_SIZE, OPTION_CANVAS_SIZE, bg_color=config.COLOR_SURFACE,
            )
            canvas.pack(pady=4)

            for widget in (card, letter, canvas):
                widget.bind("<Button-1>", lambda e, idx=i: self._select_option(idx))

            self.option_cards.append(card)
            self.option_canvases.append((canvas, screen))
            self.option_turtles.append(t)

        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(pady=(10, 10))

        self.prev_btn = GradientButton(nav_frame, "Previous", primary=False,
                                        width=150, command=self._on_previous)
        self.prev_btn.grid(row=0, column=0, padx=10)

        self.submit_btn = GradientButton(nav_frame, "Submit", primary=True,
                                          width=150, command=self._on_submit)
        self.submit_btn.grid(row=0, column=1, padx=10)

        self.next_btn = GradientButton(nav_frame, "Next", primary=True,
                                        width=150, command=self._on_next)
        self.next_btn.grid(row=0, column=2, padx=10)

        GradientButton(nav_frame, "Quit Quiz", primary=False, width=150,
                        command=self._quit_quiz).grid(row=0, column=3, padx=10)

    # ------------------------------------------------------------------
    # Question loading / rendering
    # ------------------------------------------------------------------
    def _load_question(self):
        self._stop_timer()
        question = self.controller.current_question()
        if question is None:
            self._finish_quiz()
            return

        total = len(self.controller.questions)
        self.question_label.configure(
            text=f"Question {self.controller.current_index + 1} / {total}   |   {question.difficulty}")
        self.progress.set((self.controller.current_index) / max(1, total))
        self.score_label.configure(text=f"Score: {self.controller.score}")
        self.prompt_label.configure(text=question.prompt_text)

        shape_kwargs = {"seed": question.shape_seed} if question.shape_name == "IrregularPolygon" else {}
        self.main_shape = create_shape(
            question.shape_name, self.main_turtle, size=95,
            color=config.COLOR_SHAPE_FILL, outline_color=config.COLOR_SHAPE_OUTLINE,
            **shape_kwargs,
        )
        self.main_shape.draw()

        for i, option in enumerate(question.options):
            canvas, screen = self.option_canvases[i]
            t = self.option_turtles[i]
            opt_shape_kwargs = {"seed": question.shape_seed} if question.shape_name == "IrregularPolygon" else {}
            shape = create_shape(
                question.shape_name, t, size=42,
                color=config.COLOR_SHAPE_FILL_ALT, outline_color=config.COLOR_SHAPE_OUTLINE,
                **opt_shape_kwargs,
            )
            angle = option["angle"] if option["direction"] == "Clockwise" else -option["angle"]
            shape.mirrored = option["mirrored"]
            shape.draw(angle=angle % 360, mirrored=option["mirrored"])
            self.option_shapes[i] = shape
            self.option_cards[i].configure(border_color=config.COLOR_GLASS_BORDER, border_width=1)

        already_answered = self.controller.current_index in self.controller.answers_given
        self._answered_this_view = already_answered
        self.selected_index = self.controller.answers_given.get(self.controller.current_index)

        if already_answered:
            self._show_answer_feedback(question, animate=False)
            self.timer_label.configure(text="Answered")
            self.submit_btn.configure(state="disabled")
        else:
            self.submit_btn.configure(state="normal")
            self._timer_remaining = self.timer_seconds_total
            self._update_timer_label()
            self._start_timer()
            self.controller.start_question_timer()

        self.prev_btn.configure(state=("normal" if self.controller.has_previous() else "disabled"))
        self.next_btn.configure(state=("normal" if already_answered else "disabled"))

    # ------------------------------------------------------------------
    # Timer
    # ------------------------------------------------------------------
    def _start_timer(self):
        self._tick_timer()

    def _tick_timer(self):
        self._update_timer_label()
        if self._timer_remaining <= 0:
            self._on_timeout()
            return
        self._timer_remaining -= 1
        self._timer_job = self.after(1000, self._tick_timer)

    def _stop_timer(self):
        if self._timer_job is not None:
            try:
                self.after_cancel(self._timer_job)
            except Exception:
                pass
            self._timer_job = None

    def _update_timer_label(self):
        self.timer_label.configure(text=f"\u23f1 {self._timer_remaining:02d}s")
        if self._timer_remaining <= 5:
            self.timer_label.configure(text_color=config.COLOR_ERROR)
        else:
            self.timer_label.configure(text_color=config.COLOR_WARNING)

    def _on_timeout(self):
        self._stop_timer()
        if not self._answered_this_view:
            self._on_submit(timed_out=True)

    # ------------------------------------------------------------------
    # Answer selection / submission
    # ------------------------------------------------------------------
    def _select_option(self, idx):
        if self._answered_this_view:
            return
        self.app.sound.play_click()
        self.selected_index = idx
        for i, card in enumerate(self.option_cards):
            if i == idx:
                card.configure(border_color=config.COLOR_ACCENT_BLUE, border_width=3)
            else:
                card.configure(border_color=config.COLOR_GLASS_BORDER, border_width=1)

    def _on_submit(self, timed_out=False):
        if self._answered_this_view:
            return
        self._stop_timer()
        chosen = self.selected_index if not timed_out else (self.selected_index if self.selected_index is not None else -1)
        result = self.controller.submit_answer(chosen)
        self._answered_this_view = True
        self.score_label.configure(text=f"Score: {self.controller.score}")

        if result["correct"]:
            self.app.sound.play_correct()
        else:
            self.app.sound.play_wrong()

        question = self.controller.current_question()
        self._show_answer_feedback(question, animate=True)

        self.submit_btn.configure(state="disabled")
        self.next_btn.configure(state="normal")
        self.timer_label.configure(text="Answered", text_color=config.COLOR_TEXT_SECONDARY)

    def _show_answer_feedback(self, question, animate=False):
        correct_idx = question.correct_index
        chosen_idx = self.controller.answers_given.get(self.controller.current_index)

        for i, card in enumerate(self.option_cards):
            if i == correct_idx:
                card.configure(border_color=config.COLOR_OPTION_CORRECT, border_width=3)
            elif i == chosen_idx:
                card.configure(border_color=config.COLOR_OPTION_WRONG, border_width=3)
            else:
                card.configure(border_color=config.COLOR_GLASS_BORDER, border_width=1)

        if animate:
            angle = question.rotation_angle if question.direction == "Clockwise" else -question.rotation_angle
            self.main_shape.animate_rotation(angle, steps=20, delay_ms=18)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def _on_previous(self):
        self.app.sound.play_click()
        self.controller.go_back()
        self._load_question()

    def _on_next(self):
        self.app.sound.play_click()
        if self.controller.has_next():
            self.controller.advance()
            self._load_question()
        else:
            self.controller.advance()
            self._finish_quiz()

    def _quit_quiz(self):
        self.app.sound.play_click()
        self._stop_timer()
        self.app.show_frame("home")

    def _finish_quiz(self):
        self._stop_timer()
        self.app.sound.play_complete()
        summary = self.controller.finish_and_save()
        self.app.last_result_summary = summary
        self.app.show_frame("result")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def on_destroy(self):
        self._stop_timer()
        destroy_turtle_canvas(self.main_canvas, self.main_screen)
        for canvas, screen in self.option_canvases:
            destroy_turtle_canvas(canvas, screen)
