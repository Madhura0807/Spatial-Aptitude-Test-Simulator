"""
rotation_engine.py
Pure-geometry helper functions for the rotation engine. These functions do
NOT touch Turtle directly (that's handled by Shape.animate_rotation) -- they
compute the *values* (angles, directions, mirrored flags) used to build
quiz questions and drive animations.
"""

import random

SUPPORTED_ROTATIONS = [90, 180, 270, 360]


def normalize_angle(angle):
    """Wrap an angle into the [0, 360) range."""
    return angle % 360


def signed_rotation(angle, direction):
    """Convert a magnitude + direction into a signed rotation where
    positive = clockwise (the convention used by Shape.rotate)."""
    if direction == "Clockwise":
        return angle
    return -angle


def generate_distractor_angles(correct_angle, count, angle_pool=None):
    """Generate `count` plausible-but-wrong rotation angles, distinct from
    `correct_angle` and from each other. Distractors are drawn from
    neighbouring values in the standard rotation set so they represent
    realistic mistakes (e.g. picking 90 instead of 270)."""
    angle_pool = angle_pool or SUPPORTED_ROTATIONS
    candidates = [a for a in angle_pool if normalize_angle(a) != normalize_angle(correct_angle)]
    random.shuffle(candidates)
    distractors = candidates[:count]
    # If the pool didn't have enough distinct values, synthesize offsets.
    offset = 30
    while len(distractors) < count:
        candidate = normalize_angle(correct_angle + offset)
        if candidate != normalize_angle(correct_angle) and candidate not in distractors:
            distractors.append(candidate)
        offset += 30
    return distractors[:count]


def rotation_label(angle, direction):
    """Human readable rotation description, e.g. '90 deg Clockwise'."""
    return f"{angle} deg {direction}"
