"""
shapes.py
Concrete Turtle-drawable shape classes. Every shape required by the spec
(Triangle, Square, Rectangle, Circle, Pentagon, Hexagon, Octagon, Star,
Arrow, L Shape, T Shape, Plus Shape, Flag Shape, House Shape, Chair Shape,
Irregular Polygon) is implemented here as a subclass of `Shape`.

All geometry is generated programmatically -- there are no static images.
"""

import math
import random

from src.turtle_engine.base_shape import Shape


def _regular_polygon_vertices(n, radius, start_angle_deg=90):
    """Vertices of a regular n-gon of the given circumradius, centered at
    the origin, with the first vertex at `start_angle_deg`."""
    verts = []
    for i in range(n):
        angle = math.radians(start_angle_deg + i * (360 / n))
        verts.append((radius * math.cos(angle), radius * math.sin(angle)))
    return verts


# --------------------------------------------------------------------------
# Regular polygon based shapes
# --------------------------------------------------------------------------
class Triangle(Shape):
    display_name = "Triangle"
    real_life_examples = ["Traffic yield signs", "Pyramids", "Set squares", "Roof trusses"]

    def _generate_vertices(self):
        return _regular_polygon_vertices(3, self.size)

    def lines_of_symmetry(self):
        return 3

    def rotational_symmetry_order(self):
        return 3


class Square(Shape):
    display_name = "Square"
    real_life_examples = ["Chess board squares", "Windows", "Floor tiles", "Picture frames"]

    def _generate_vertices(self):
        h = self.size * 0.75
        return [(h, h), (-h, h), (-h, -h), (h, -h)]

    def lines_of_symmetry(self):
        return 4

    def rotational_symmetry_order(self):
        return 4


class Rectangle(Shape):
    display_name = "Rectangle"
    real_life_examples = ["Doors", "Books", "Mobile phone screens", "Bricks"]

    def _generate_vertices(self):
        w = self.size * 1.1
        h = self.size * 0.6
        return [(w, h), (-w, h), (-w, -h), (w, -h)]

    def lines_of_symmetry(self):
        return 2

    def rotational_symmetry_order(self):
        return 2


class Circle(Shape):
    """Approximated with a high vertex-count polygon so the shared
    rotation/animation engine works uniformly, while still visually
    reading as a circle."""
    display_name = "Circle"
    real_life_examples = ["Wheels", "Coins", "Clocks", "The Sun"]

    def _generate_vertices(self):
        return _regular_polygon_vertices(36, self.size)

    def num_sides(self):
        return 0

    def num_vertices(self):
        return 0

    def lines_of_symmetry(self):
        return float("inf")

    def rotational_symmetry_order(self):
        return float("inf")

    def interior_angle(self):
        return None

    def exterior_angle(self):
        return None


class Pentagon(Shape):
    display_name = "Pentagon"
    real_life_examples = ["The Pentagon building", "Home plate in baseball", "Soccer ball panels"]

    def _generate_vertices(self):
        return _regular_polygon_vertices(5, self.size)

    def lines_of_symmetry(self):
        return 5

    def rotational_symmetry_order(self):
        return 5


class Hexagon(Shape):
    display_name = "Hexagon"
    real_life_examples = ["Honeycomb cells", "Nuts/bolts heads", "Snowflakes"]

    def _generate_vertices(self):
        return _regular_polygon_vertices(6, self.size)

    def lines_of_symmetry(self):
        return 6

    def rotational_symmetry_order(self):
        return 6


class Octagon(Shape):
    display_name = "Octagon"
    real_life_examples = ["Stop signs", "Umbrellas", "Gazebos"]

    def _generate_vertices(self):
        return _regular_polygon_vertices(8, self.size)

    def lines_of_symmetry(self):
        return 8

    def rotational_symmetry_order(self):
        return 8


class Star(Shape):
    display_name = "Star"
    real_life_examples = ["Night sky stars", "National flags", "Sheriff badges", "Awards"]

    def _generate_vertices(self):
        outer = self.size
        inner = self.size * 0.42
        verts = []
        for i in range(10):
            radius = outer if i % 2 == 0 else inner
            angle = math.radians(90 + i * 36)
            verts.append((radius * math.cos(angle), radius * math.sin(angle)))
        return verts

    def num_sides(self):
        return 5

    def lines_of_symmetry(self):
        return 5

    def rotational_symmetry_order(self):
        return 5

    def interior_angle(self):
        return 36.0

    def exterior_angle(self):
        return None


# --------------------------------------------------------------------------
# Custom polygon shapes (asymmetric -> good rotation test candidates)
# --------------------------------------------------------------------------
class Arrow(Shape):
    display_name = "Arrow"
    real_life_examples = ["Road direction signs", "Compass needles", "Cursor pointers"]

    def _generate_vertices(self):
        s = self.size
        return [
            (0, s), (-0.6 * s, 0.15 * s), (-0.25 * s, 0.15 * s),
            (-0.25 * s, -s), (0.25 * s, -s), (0.25 * s, 0.15 * s),
            (0.6 * s, 0.15 * s),
        ]

    def lines_of_symmetry(self):
        return 1

    def rotational_symmetry_order(self):
        return 1


class LShape(Shape):
    display_name = "L Shape"
    real_life_examples = ["L-shaped sofas", "Corner shelves", "Tetris 'L' piece"]

    def _generate_vertices(self):
        s = self.size * 0.55
        return [
            (-s, s), (-s / 3, s), (-s / 3, -s / 3), (s, -s / 3),
            (s, -s), (-s, -s),
        ]

    def lines_of_symmetry(self):
        return 0

    def rotational_symmetry_order(self):
        return 1


class TShape(Shape):
    display_name = "T Shape"
    real_life_examples = ["T-junctions on roads", "Wrenches", "Tetris 'T' piece"]

    def _generate_vertices(self):
        s = self.size * 0.55
        return [
            (-s, s), (s, s), (s, s / 3), (s / 3, s / 3),
            (s / 3, -s), (-s / 3, -s), (-s / 3, s / 3), (-s, s / 3),
        ]

    def lines_of_symmetry(self):
        return 1

    def rotational_symmetry_order(self):
        return 1


class PlusShape(Shape):
    display_name = "Plus Shape"
    real_life_examples = ["Medical / first-aid cross", "Plus/addition symbol", "Window mullions"]

    def _generate_vertices(self):
        s = self.size * 0.55
        a = s / 3
        return [
            (-a, s), (a, s), (a, a), (s, a), (s, -a), (a, -a),
            (a, -s), (-a, -s), (-a, -a), (-s, -a), (-s, a), (-a, a),
        ]

    def lines_of_symmetry(self):
        return 4

    def rotational_symmetry_order(self):
        return 4


class FlagShape(Shape):
    display_name = "Flag Shape"
    real_life_examples = ["National flags on poles", "Golf course flags", "Nautical signal flags"]

    def _generate_vertices(self):
        s = self.size
        pole_w = s * 0.08
        return [
            (-pole_w, s), (pole_w, s), (pole_w, s * 0.15),
            (s * 0.9, -s * 0.1), (pole_w, -s * 0.35), (pole_w, -s),
            (-pole_w, -s),
        ]

    def lines_of_symmetry(self):
        return 0

    def rotational_symmetry_order(self):
        return 1


class HouseShape(Shape):
    display_name = "House Shape"
    real_life_examples = ["Pictogram house icons", "Simple roof architecture", "Birdhouses"]

    def _generate_vertices(self):
        s = self.size * 0.7
        return [
            (0, s * 1.3), (s, s * 0.4), (s * 0.65, s * 0.4),
            (s * 0.65, -s), (-s * 0.65, -s), (-s * 0.65, s * 0.4),
            (-s, s * 0.4),
        ]

    def lines_of_symmetry(self):
        return 1

    def rotational_symmetry_order(self):
        return 1


class ChairShape(Shape):
    display_name = "Chair Shape"
    real_life_examples = ["Office chairs (side profile)", "Furniture icons/pictograms"]

    def _generate_vertices(self):
        s = self.size * 0.6
        return [
            (-s, s), (-s * 0.6, s), (-s * 0.6, s * 0.1), (s * 0.6, s * 0.1),
            (s * 0.6, s), (s, s), (s, -s * 0.1), (s * 0.6, -s * 0.1),
            (s * 0.6, -s), (s * 0.2, -s), (s * 0.2, -s * 0.35),
            (-s * 0.6, -s * 0.35), (-s * 0.6, -s), (-s, -s),
        ]

    def lines_of_symmetry(self):
        return 0

    def rotational_symmetry_order(self):
        return 1


class IrregularPolygon(Shape):
    """A randomly generated, irregular (but reproducible) polygon used for
    the hardest 'Expert' difficulty questions where users cannot rely on
    obvious symmetry cues."""
    display_name = "Irregular Polygon"
    real_life_examples = ["Freeform map/plot boundaries", "Puzzle pieces", "Abstract art shapes"]

    def __init__(self, turtle_obj, size=100, color="#4F7CFF",
                 outline_color="#F2F3FA", center=(0, 0), seed=None, num_points=7):
        self._seed = seed if seed is not None else random.randint(0, 999999)
        self._num_points = num_points
        super().__init__(turtle_obj, size, color, outline_color, center)

    def _generate_vertices(self):
        rng = random.Random(self._seed)
        n = self._num_points
        verts = []
        for i in range(n):
            base_angle = 360 / n * i
            angle_jitter = rng.uniform(-12, 12)
            radius_jitter = rng.uniform(0.55, 1.0)
            angle = math.radians(base_angle + angle_jitter)
            radius = self.size * radius_jitter
            verts.append((radius * math.cos(angle), radius * math.sin(angle)))
        return verts

    def lines_of_symmetry(self):
        return 0

    def rotational_symmetry_order(self):
        return 1


# --------------------------------------------------------------------------
# Registry used by the question generator / learn mode to instantiate
# shapes dynamically by name.
# --------------------------------------------------------------------------
SHAPE_REGISTRY = {
    "Triangle": Triangle,
    "Square": Square,
    "Rectangle": Rectangle,
    "Circle": Circle,
    "Pentagon": Pentagon,
    "Hexagon": Hexagon,
    "Octagon": Octagon,
    "Star": Star,
    "Arrow": Arrow,
    "LShape": LShape,
    "TShape": TShape,
    "PlusShape": PlusShape,
    "FlagShape": FlagShape,
    "HouseShape": HouseShape,
    "ChairShape": ChairShape,
    "IrregularPolygon": IrregularPolygon,
}


def create_shape(name, turtle_obj, size=100, color="#4F7CFF",
                  outline_color="#F2F3FA", center=(0, 0), **kwargs):
    """Factory: instantiate a shape by its registry name."""
    cls = SHAPE_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown shape: {name}")
    return cls(turtle_obj, size=size, color=color, outline_color=outline_color,
               center=center, **kwargs)
