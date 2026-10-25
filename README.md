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

## Play in your browser (no install)

**<https://orcasound.github.io/thewhale-clicks/>**

Same game, nothing to install. It runs on phones and tablets too (on an
iPhone or iPad, turn off the silent switch). The page is `index.html`; it
loads the sounds from `ScottsClicks/`, so to try it locally serve the folder
(`python3 -m http.server`, then open <http://localhost:8000>) rather than
opening the file directly.

The rest of this README is for running the desktop version.

## Setup

Requires Python 3.8+ with Tkinter, plus `git`. The Python packages
(`numpy`, `pygame`) are installed from `requirements.txt`.

### 1. Install the prerequisites for your system

**Ubuntu / Debian**

```bash
sudo apt update
sudo apt install git python3 python3-venv python3-pip python3-tk
```

**macOS**

- Install Python 3 from [python.org](https://www.python.org/downloads/macos/);
  that installer includes Tkinter. `git` comes with the Xcode command-line
  tools (`xcode-select --install`).
- If you use Homebrew instead: `brew install git python python-tk`.

**Windows**

- Install Python 3 from [python.org](https://www.python.org/downloads/windows/).
  In the installer, tick **Add python.exe to PATH** and keep
  **tcl/tk and IDLE** selected (that is Tkinter).
- Install [Git for Windows](https://git-scm.com/download/win).

**iOS / iPadOS** is not supported: the trainer is a Tkinter desktop app and
needs a computer running Linux, macOS or Windows.

### 2. Clone the repository

```bash
git clone https://github.com/orcasound/thewhale-clicks.git
cd thewhale-clicks
```

### 3. Create a virtual environment and install the requirements

Ubuntu / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (Command Prompt or PowerShell):

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If PowerShell refuses to run the activate script, run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then try again.

To check that Tkinter is available: `python -m tkinter` should open a small
test window.

Activate the virtual environment again (the `activate` line above) each time
you open a new terminal to run the trainer.

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

        Volume %  [-] ===o======== [+]
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

**Volume** runs from 0% to 400%. It multiplies the sound samples themselves,
not the player volume, so you can boost these quiet recordings above their
original level. All nine clips are normalized to the same peak level (that of
the loudest recording) so loudness doesn't give away the answer; 100% plays
them at that level.

Suggested progression: master each column, then each row, then the full quiz.

## Settings

The number of questions and the pause between them are constants at the top
of `click_trainer.py` (`NUM_TRIALS`, `NEXT_DELAY_MS`), as is the top of the volume range
(`MAX_GAIN_PCT`).
