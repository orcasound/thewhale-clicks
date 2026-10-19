"""Echolocation click ear-training game.

A 3x3 matrix of sounds: columns are visitors (whales clicking in a low, mid
or high frequency range), rows are targets (salmon, seal, squid).

Learn mode: press any Play button to hear that sound.
Quiz mode:  press a Q button to quiz yourself on a column, a row, or all
            nine sounds. A sound plays; answer by pressing the Play button
            you think made it.
"""

import random
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

import pygame

SOUND_DIR = Path(__file__).resolve().parent / "ScottsClicks"

# Columns (visitors) and rows (targets), and how they map to file names.
VISITORS = [("A", "low"), ("B", "mid"), ("C", "high")]
TARGETS = [("1", "salmon"), ("2", "seal"), ("3", "squid")]

NUM_TRIALS = 10        # questions per quiz
NEXT_DELAY_MS = 1000   # pause after an answer before the next sound plays
FIRST_DELAY_MS = 500   # pause before the first sound of a quiz

COLOR_IDLE = "#d9d9d9"
COLOR_CHOICE = "#cfe2ff"
COLOR_RIGHT = "#7bd389"
COLOR_WRONG = "#f28b82"
# Hover colours. Tk draws a button under the mouse in its activebackground,
# so result colours must set it too or the clicked button never shows them.
HOVER = {COLOR_IDLE: "#ececec", COLOR_CHOICE: "#a8c8ff"}


def sound_path(row, col):
    return SOUND_DIR / f"echo-{VISITORS[col][1]}-clicker-{TARGETS[row][1]}.mp3"


def sound_name(cell):
    row, col = cell
    return f"{VISITORS[col][0]}{TARGETS[row][0]} ({VISITORS[col][1]} / {TARGETS[row][1]})"


def paint(btn, color):
    btn.config(bg=color, activebackground=HOVER.get(color, color))


def letter_grade(pct):
    for cutoff, letter in ((90, "A"), (80, "B"), (70, "C"), (60, "D")):
        if pct >= cutoff:
            return letter
    return "F"


class ClickTrainer:
    def __init__(self, root):
        self.root = root
        root.title("Echolocation Click Trainer")

        pygame.mixer.init()
        self.sounds = {}
        for r in range(3):
            for c in range(3):
                path = sound_path(r, c)
                if not path.exists():
                    messagebox.showerror("Missing sound", f"Could not find:\n{path}")
                    sys.exit(1)
                self.sounds[(r, c)] = pygame.mixer.Sound(str(path))

        # Quiz state
        self.quiz_active = False
        self.quiz_title = ""
        self.candidates = []
        self.trials = []
        self.trial_index = 0
        self.current = None
        self.awaiting_answer = False
        self.results = []          # list of (played_cell, answered_cell)
        self.pending_after = None

        self.volume = tk.IntVar(value=70)
        self._build_ui()
        self.set_volume()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        grid = tk.Frame(self.root, padx=16, pady=12)
        grid.pack()

        tk.Label(grid, text="Visitor", font=("TkDefaultFont", 12, "bold")).grid(
            row=0, column=2, columnspan=3)
        for c, (letter, freq) in enumerate(VISITORS):
            tk.Label(grid, text=f"{letter}\n({freq})").grid(row=1, column=2 + c)

        tk.Label(grid, text="Target", font=("TkDefaultFont", 12, "bold")).grid(
            row=2, column=0, rowspan=3, padx=(0, 8))
        for r, (num, name) in enumerate(TARGETS):
            tk.Label(grid, text=f"{num} {name}", anchor="e", width=9).grid(
                row=2 + r, column=1, sticky="e")

        self.play_buttons = {}
        for r in range(3):
            for c in range(3):
                btn = tk.Button(grid, text="P", width=6, height=2,
                                command=lambda cell=(r, c): self.on_play(cell))
                paint(btn, COLOR_IDLE)
                btn.grid(row=2 + r, column=2 + c, padx=4, pady=4)
                self.play_buttons[(r, c)] = btn

        self.quiz_buttons = []
        for r in range(3):
            cells = [(r, c) for c in range(3)]
            self._quiz_button(grid, 2 + r, 5, cells, f"Target {TARGETS[r][0]} ({TARGETS[r][1]})")
        for c in range(3):
            cells = [(r, c) for r in range(3)]
            self._quiz_button(grid, 5, 2 + c, cells, f"Visitor {VISITORS[c][0]} ({VISITORS[c][1]})")
        all_cells = [(r, c) for r in range(3) for c in range(3)]
        self._quiz_button(grid, 5, 5, all_cells, "All sounds")

        # Status / quiz controls
        status = tk.Frame(self.root, padx=16)
        status.pack(fill="x")
        self.mode_label = tk.Label(status, text="Learn mode: press P to hear a sound",
                                   font=("TkDefaultFont", 11, "bold"))
        self.mode_label.pack()
        self.status_label = tk.Label(status, text="Press a Q button to start a quiz")
        self.status_label.pack()
        controls = tk.Frame(status)
        controls.pack(pady=4)
        self.replay_button = tk.Button(controls, text="Replay sound", state="disabled",
                                       command=self.replay)
        self.replay_button.pack(side="left", padx=4)
        self.stop_button = tk.Button(controls, text="Stop quiz", state="disabled",
                                     command=self.stop_quiz)
        self.stop_button.pack(side="left", padx=4)

        # Volume
        vol = tk.Frame(self.root, padx=16, pady=10)
        vol.pack()
        tk.Label(vol, text="Volume").pack(side="left")
        tk.Button(vol, text="−", width=3, command=lambda: self.nudge_volume(-10)).pack(side="left")
        tk.Scale(vol, from_=0, to=100, orient="horizontal", length=200,
                 variable=self.volume, command=lambda _v: self.set_volume()).pack(side="left")
        tk.Button(vol, text="+", width=3, command=lambda: self.nudge_volume(10)).pack(side="left")

    def _quiz_button(self, parent, row, col, cells, title):
        btn = tk.Button(parent, text="Q", width=6, height=2,
                        command=lambda: self.start_quiz(cells, title))
        btn.grid(row=row, column=col, padx=4, pady=4)
        self.quiz_buttons.append(btn)

    def set_volume(self):
        level = self.volume.get() / 100
        for snd in self.sounds.values():
            snd.set_volume(level)

    def nudge_volume(self, delta):
        self.volume.set(max(0, min(100, self.volume.get() + delta)))
        self.set_volume()

    def play(self, cell):
        pygame.mixer.stop()
        self.sounds[cell].play()

    def color_buttons(self):
        for cell, btn in self.play_buttons.items():
            if self.quiz_active:
                enabled = cell in self.candidates
                paint(btn, COLOR_CHOICE if enabled else COLOR_IDLE)
                btn.config(state="normal" if enabled else "disabled")
            else:
                paint(btn, COLOR_IDLE)
                btn.config(state="normal")

    # ---------------------------------------------------------------- Learn
    def on_play(self, cell):
        if not self.quiz_active:
            self.play(cell)
        elif self.awaiting_answer:
            self.answer(cell)

    # ----------------------------------------------------------------- Quiz
    def start_quiz(self, cells, title):
        self.quiz_active = True
        self.quiz_title = title
        self.candidates = cells
        # Balanced random order: every candidate appears about equally often.
        pool = []
        while len(pool) < NUM_TRIALS:
            block = list(cells)
            random.shuffle(block)
            pool.extend(block)
        self.trials = pool[:NUM_TRIALS]
        self.trial_index = 0
        self.results = []

        self.mode_label.config(text=f"Quiz mode: {title}")
        for btn in self.quiz_buttons:
            btn.config(state="disabled")
        self.stop_button.config(state="normal")
        self.color_buttons()
        self.status_label.config(text="Get ready...")
        self.pending_after = self.root.after(FIRST_DELAY_MS, self.next_trial)

    def next_trial(self):
        self.pending_after = None
        if self.trial_index >= NUM_TRIALS:
            self.finish_quiz()
            return
        self.color_buttons()
        self.current = self.trials[self.trial_index]
        self.awaiting_answer = True
        self.replay_button.config(state="normal")
        self.status_label.config(
            text=f"Sound {self.trial_index + 1} of {NUM_TRIALS}: which one was it?")
        self.play(self.current)

    def replay(self):
        if self.quiz_active and self.current is not None:
            self.play(self.current)

    def answer(self, cell):
        self.awaiting_answer = False
        self.replay_button.config(state="disabled")
        self.results.append((self.current, cell))
        correct = cell == self.current
        if correct:
            paint(self.play_buttons[cell], COLOR_RIGHT)
            self.status_label.config(text="Correct!")
        else:
            paint(self.play_buttons[cell], COLOR_WRONG)
            paint(self.play_buttons[self.current], COLOR_RIGHT)
            self.status_label.config(text=f"No, that was {sound_name(self.current)}")
        self.trial_index += 1
        self.pending_after = self.root.after(NEXT_DELAY_MS, self.next_trial)

    def finish_quiz(self):
        right = sum(1 for played, answered in self.results if played == answered)
        pct = round(100 * right / len(self.results))
        lines = [f"{self.quiz_title}",
                 f"Score: {right} / {len(self.results)}  ({pct}%)",
                 f"Grade: {letter_grade(pct)}"]
        mistakes = [(p, a) for p, a in self.results if p != a]
        if mistakes:
            lines.append("\nMistakes:")
            for played, answered in mistakes:
                lines.append(f"  played {sound_name(played)}\n    you chose {sound_name(answered)}")
        self.end_quiz()
        self.status_label.config(text=f"Last quiz: {right}/{len(self.results)} "
                                      f"({pct}%) grade {letter_grade(pct)}")
        messagebox.showinfo("Quiz results", "\n".join(lines))

    def stop_quiz(self):
        self.end_quiz()
        self.status_label.config(text="Quiz stopped. Press a Q button to start a quiz")

    def end_quiz(self):
        if self.pending_after is not None:
            self.root.after_cancel(self.pending_after)
            self.pending_after = None
        pygame.mixer.stop()
        self.quiz_active = False
        self.awaiting_answer = False
        self.current = None
        self.mode_label.config(text="Learn mode: press P to hear a sound")
        for btn in self.quiz_buttons:
            btn.config(state="normal")
        self.replay_button.config(state="disabled")
        self.stop_button.config(state="disabled")
        self.color_buttons()


def main():
    root = tk.Tk()
    ClickTrainer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
