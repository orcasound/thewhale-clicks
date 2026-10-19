# Echolocation Click Trainer

An ear-training game for learning to tell apart echolocation clicks.

The nine sounds in `ScottsClicks/` form a 3 × 3 matrix:

|                | Visitor A (low) | Visitor B (mid) | Visitor C (high) |
|----------------|-----------------|-----------------|------------------|
| **Target 1 – salmon** | A1 | B1 | C1 |
| **Target 2 – seal**   | A2 | B2 | C2 |
| **Target 3 – squid**  | A3 | B3 | C3 |

Each visitor is a whale clicking in a slightly different frequency range;
each target is a different echo.

## Setup

Requires Python 3.8+ with Tkinter.
On Debian/Ubuntu, install Tkinter with `sudo apt install python3-tk` if needed.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python click_trainer.py
```

## How to play

```
                 Visitor
              A     B     C
        1     P     P     P     Q
Target  2     P     P     P     Q
        3     P     P     P     Q
              Q     Q     Q     Q

        Volume  [-] ======o==== [+]
```

**Learn mode** (the default): press any **P** button to hear that sound.

**Quiz mode**: press a **Q** button.

- **Q under a column** quizzes the three targets for that visitor
  (start here: same whale, different echoes).
- **Q at the end of a row** quizzes the three visitors for that target
  (same echo, different whales).
- **Q in the bottom-right corner** quizzes all nine sounds.

During a quiz only the buttons in play are enabled (shaded blue). A sound
plays; press the **P** button you think made it. Your choice turns green if
right, or red with the correct answer shown in green. The next sound plays one
second later. Use **Replay sound** to hear the current one again, or
**Stop quiz** to quit early.

After 10 sounds you get a score, a letter grade (A ≥ 90%, B ≥ 80%, C ≥ 70%,
D ≥ 60%), and a list of the sounds you confused.

Suggested progression: master each column, then each row, then the full quiz.

## Settings

The number of questions and the pause between them are constants at the top
of `click_trainer.py` (`NUM_TRIALS`, `NEXT_DELAY_MS`).
