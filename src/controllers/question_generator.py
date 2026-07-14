"""
question_generator.py
Builds randomized spatial-rotation questions: picks a shape, a target
rotation (angle + direction), the correct answer, and three realistic
wrong options (no duplicates), scaled by difficulty level.
"""

import random

from src import config
from src.turtle_engine.rotation_engine import (
    SUPPORTED_ROTATIONS,
    generate_distractor_angles,
)


class Question:
    """Value object describing a single quiz question."""

    def __init__(self, shape_name, rotation_angle, direction, options,
                 correct_index, difficulty, shape_seed=None):
        self.shape_name = shape_name
        self.rotation_angle = rotation_angle
        self.direction = direction
        # options: list of dicts {angle, direction, mirrored, is_correct}
        self.options = options
        self.correct_index = correct_index
        self.difficulty = difficulty
        self.shape_seed = shape_seed  # for IrregularPolygon reproducibility

    @property
    def prompt_text(self):
        return f"Rotate the figure by {self.rotation_angle}\u00b0 {self.direction}"


class QuestionGenerator:
    """Generates a stream of non-repeating spatial rotation questions for a
    given difficulty level."""

    def __init__(self, difficulty=config.DEFAULT_DIFFICULTY):
        self.set_difficulty(difficulty)
        self._recent_shapes = []

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty if difficulty in config.DIFFICULTY_PRESETS else config.DEFAULT_DIFFICULTY
        self.preset = config.DIFFICULTY_PRESETS[self.difficulty]

    def _pick_shape(self):
        pool = self.preset["shape_pool"]
        choices = [s for s in pool if s not in self._recent_shapes[-2:]] or pool
        shape = random.choice(choices)
        self._recent_shapes.append(shape)
        return shape

    def generate_question(self):
        shape_name = self._pick_shape()
        angle = random.choice(self.preset["angles"])
        direction = random.choice(config.ROTATION_DIRECTIONS)

        correct_option = {
            "angle": angle, "direction": direction,
            "mirrored": False, "is_correct": True,
        }

        num_distractors = 3
        distractor_angles = generate_distractor_angles(
            angle, num_distractors, angle_pool=SUPPORTED_ROTATIONS
        )

        options = [correct_option]
        use_mirrored = self.preset["use_mirrored_distractors"]
        for i, d_angle in enumerate(distractor_angles):
            mirrored = use_mirrored and i == 0  # one flipped distractor, if enabled
            d_direction = direction if mirrored else random.choice(config.ROTATION_DIRECTIONS)
            options.append({
                "angle": d_angle, "direction": d_direction,
                "mirrored": mirrored, "is_correct": False,
            })

        random.shuffle(options)
        correct_index = next(i for i, o in enumerate(options) if o["is_correct"])

        shape_seed = random.randint(0, 999999) if shape_name == "IrregularPolygon" else None

        return Question(
            shape_name=shape_name,
            rotation_angle=angle,
            direction=direction,
            options=options,
            correct_index=correct_index,
            difficulty=self.difficulty,
            shape_seed=shape_seed,
        )

    def generate_batch(self, count):
        return [self.generate_question() for _ in range(count)]
