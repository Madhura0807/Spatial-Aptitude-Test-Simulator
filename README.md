# Spatial Aptitude Test Simulator

An interactive **Spatial Reasoning / Mental Rotation** aptitude test simulator,
built as a 3rd-year B.Tech mini project. It recreates the shape-rotation
questions commonly seen in placement aptitude tests (TCS, Infosys, Accenture,
Capgemini, Cognizant, Deloitte, Wipro, etc.) with a modern, dark-mode,
glassmorphism desktop interface.

Every geometric figure — Triangle, Square, Rectangle, Circle, Pentagon,
Hexagon, Octagon, Star, Arrow, L Shape, T Shape, Plus Shape, Flag Shape,
House Shape, Chair Shape and randomised Irregular Polygons — is drawn and
rotated **programmatically with Python's `turtle` module**, embedded inside a
CustomTkinter desktop application. No static images are used anywhere.

---

## Features

- **Quiz Mode** — timed, scored, 5/10/15/20-question rotation quizzes across
  four difficulty levels (Easy, Medium, Hard, Expert), with Previous / Next /
  Submit navigation and a live rotation-animation reveal of the correct answer.
- **Practice Mode** — unlimited untimed questions with instant, plain-English
  explanations and an animated correct-answer reveal.
- **Learn Mode** — browse every shape, inspect sides, vertices, lines of
  symmetry, rotational symmetry order, interior/exterior angles and real-life
  examples, and trigger a full 360° rotation demo.
- **Previous Scores & Statistics** — full quiz history, overall accuracy,
  average response time, strongest/weakest shapes, and unlocked achievements.
- **Leaderboard** — Highest Score, Fastest Completion and Best Accuracy tabs,
  backed by SQLite.
- **Settings** — theme, default difficulty, timer duration, question count,
  and a sound-effects toggle, persisted between runs.
- **Turtle-drawn animated logo, animated geometric backgrounds, confetti on a
  perfect score, achievement badges, and synthesized (no-internet-required)
  sound effects for clicks, correct/wrong answers and quiz completion.**

---

## Tech Stack

| Layer          | Technology                              |
|----------------|------------------------------------------|
| Graphics engine| `turtle` (`RawTurtle` embedded via `TurtleScreen` inside Tkinter canvases) |
| GUI            | `customtkinter`, `tkinter`               |
| Database       | `sqlite3`                                |
| Architecture   | OOP, modular packages, MVC-style split (models / controllers / ui) |

---

## Project Structure

```
SpatialAptitudeTest/
├── assets/
│   ├── icons/
│   └── sounds/              # synthesized on first run (no external files needed)
├── database/
│   └── spatial_aptitude.db  # created automatically on first run
├── src/
│   ├── config.py            # theme, colors, fonts, difficulty presets
│   ├── turtle_engine/
│   │   ├── base_shape.py    # abstract Shape (draw/rotate/animate_rotation/...)
│   │   ├── shapes.py        # every concrete shape + factory
│   │   ├── canvas_manager.py# embeds RawTurtle inside Tkinter frames
│   │   └── rotation_engine.py
│   ├── models/
│   │   └── database.py      # SQLite schema + queries
│   ├── controllers/
│   │   ├── question_generator.py
│   │   ├── quiz_controller.py
│   │   └── stats_controller.py
│   ├── ui/
│   │   ├── app.py           # window + screen router
│   │   ├── widgets.py        # GlassCard, GradientButton, AnimatedBackground...
│   │   ├── splash_screen.py
│   │   ├── home_screen.py
│   │   ├── instructions_screen.py
│   │   ├── quiz_screen.py
│   │   ├── practice_screen.py
│   │   ├── learn_screen.py
│   │   ├── result_screen.py
│   │   ├── leaderboard_screen.py
│   │   ├── previous_scores_screen.py
│   │   └── settings_screen.py
│   └── utils/
│       ├── sound_manager.py # synthesizes + plays WAV tones
│       └── helpers.py       # settings JSON load/save, formatting
├── main.py
├── requirements.txt
└── README.md
```

---

## Setup & Run

1. **Requirements:** Python 3.10+ (3.12 recommended) with Tkinter available.
   - Windows / macOS official installers include Tkinter by default.
   - On Debian/Ubuntu, if `import tkinter` fails, install it with:
     ```
     sudo apt install python3-tk
     ```

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```
   python main.py
   ```

On first launch the app will automatically:
- create `database/spatial_aptitude.db` with all required tables, and
- synthesize the click / correct / wrong / completion WAV sound effects into
  `assets/sounds/` (pure Python, no internet connection required).

---

## Application Flow

```
Splash Screen → Home Dashboard → Instructions → Quiz → Result Screen → Leaderboard
                        ├── Practice Mode
                        ├── Learn Shapes
                        ├── Previous Scores
                        └── Settings
```

---

## Database Schema (SQLite)

- **Users** — id, username, created_at
- **Scores** — per-session score, accuracy, avg response time, streak, difficulty
- **QuizHistory** — one row per completed Quiz/Practice session
- **QuestionHistory** — one row per answered question (shape, rotation, correctness, response time)
- **Achievements** — unlocked badges per user (Perfect Score, On Fire, Expert Navigator, ...)

---

## Notes for Evaluators

- All shapes are generated from first principles (vertex coordinates +
  rotation matrices) inside `src/turtle_engine/shapes.py` — nothing is a
  pre-rendered image.
- Rotation animation is implemented in `Shape.animate_rotation()`
  (`src/turtle_engine/base_shape.py`) using Tkinter's non-blocking
  `screen.ontimer` scheduling so the GUI remains fully responsive during
  animation.
- The question generator (`src/controllers/question_generator.py`) creates
  one correct option and three distinct, realistic wrong options (including
  an occasional mirrored/flipped distractor on Medium+ difficulty) with no
  duplicate options.
