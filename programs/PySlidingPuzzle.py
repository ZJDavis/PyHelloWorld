# -*- coding: utf-8 -*-
# programs/PySlidingPuzzle.py

"""
Sliding Puzzle Game


- Auto-discovered by main menu
- Uses tkinter for UI
- Supports image-based or generated puzzles
- Adjustable grid size (3-8 per dimension)
- Mouse + keyboard controls
- Timer starts on first move
- Persistent top-10 leaderboard per grid size


Python >= 3.10
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Tuple
import tkinter as tk
from tkinter import simpledialog, messagebox

from PyProgramBase import ProgramBase


ASSETS_DIR = Path("assets/SlidingPuzzleImages")
LEADERBOARD_FILE = Path("sliding_puzzle_leaderboard.json")
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


class SlidingPuzzleProgram(ProgramBase):
    def run(self):
        rows, cols = self._prompt_grid_size()
        image = self._load_or_generate_image(rows, cols)

        game = SlidingPuzzleGame(rows, cols, image)
        game.start()


class SlidingPuzzleGame:
    TILE_SIZE = 100

    def __init__(self, rows: int, cols: int, image: tk.PhotoImage):
        self.rows = rows
        self.cols = cols
        self.image = image

        # Store tile images
        self.tile_images = self._create_tile_images()

        self.root = tk.Tk()
        self.root.title("Sliding Puzzle")

        self.canvas = tk.Canvas(
            self.root,
            width=self.cols * self.TILE_SIZE,
            height=self.rows * self.TILE_SIZE,
        )
        self.canvas.pack()

        self.start_time: float | None = None
        self.solved = False

        self.tiles, self.empty_pos = self._create_tiles()
        self._shuffle_tiles()
        self._draw()

        self.canvas.bind("<Button-1>", self._on_click)
        self.root.bind("<Key>", self._on_key)

    def start(self):
        self.root.mainloop()

    def _create_tiles(self):
        tiles = []
        for r in range(self.rows):
            for c in range(self.cols):
                if r == 0 and c == self.cols - 1:
                    tiles.append(None)
                else:
                    tiles.append((r, c))
        return tiles, (0, self.cols - 1)

    def _shuffle_tiles(self):
        movable = [t for t in self.tiles if t is not None]
        random.shuffle(movable)

        i = 0
        for idx in range(len(self.tiles)):
            if self.tiles[idx] is not None:
                self.tiles[idx] = movable[i]
                i += 1

    def _create_tile_images(self):
        """Create individual PhotoImage objects for each tile"""
        tile_images = {}
        for r in range(self.rows):
            for c in range(self.cols):
                # Create a new PhotoImage with just the tile portion
                tile_img = tk.PhotoImage()
                tile_img.tk.call(tile_img, 'copy', self.image, 
                                '-from', c * self.TILE_SIZE, r * self.TILE_SIZE,
                                (c + 1) * self.TILE_SIZE, (r + 1) * self.TILE_SIZE,
                                '-to', 0, 0)
                tile_images[(r, c)] = tile_img
        return tile_images

    def _draw(self):
        self.canvas.delete("all")
        for idx, tile in enumerate(self.tiles):
            r, c = divmod(idx, self.cols)
            x0 = c * self.TILE_SIZE
            y0 = r * self.TILE_SIZE

            if tile is None:
                continue

            tr, tc = tile
            self.canvas.create_image(
                x0,
                y0,
                image=self.image,
                anchor="nw",
                source=(
                    tc * self.TILE_SIZE,
                    tr * self.TILE_SIZE,
                    self.TILE_SIZE,
                    self.TILE_SIZE,
                ),
            )

    def _on_click(self, event):
        c = event.x // self.TILE_SIZE
        r = event.y // self.TILE_SIZE
        self._try_move((r, c))

    def _on_key(self, event):
        er, ec = self.empty_pos
        moves = {
            "Up": (er + 1, ec),
            "Down": (er - 1, ec),
            "Left": (er, ec + 1),
            "Right": (er, ec - 1),
        }
        if event.keysym in moves:
            self._try_move(moves[event.keysym])

    def _try_move(self, pos: Tuple[int, int]):
        if self.solved:
            return

        r, c = pos
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return

        er, ec = self.empty_pos
        if abs(er - r) + abs(ec - c) != 1:
            return

        if self.start_time is None:
            self.start_time = time.time()

        empty_idx = er * self.cols + ec
        tile_idx = r * self.cols + c
        self.tiles[empty_idx], self.tiles[tile_idx] = (
            self.tiles[tile_idx],
            None,
        )
        self.empty_pos = (r, c)

        self._draw()

        if self._is_solved():
            self._on_solved()

    def _is_solved(self) -> bool:
        for idx, tile in enumerate(self.tiles):
            if tile is None:
                continue
            if tile != divmod(idx, self.cols):
                return False
        return True

    def _on_solved(self):
        self.solved = True
        elapsed = time.time() - self.start_time
        initials = simpledialog.askstring("Solved!", f"Time: {elapsed:.2f}s\nEnter initials:")
        if initials:
            Leaderboard.record(self.rows, self.cols, elapsed, initials)
        messagebox.showinfo("Completed", f"Puzzle solved in {elapsed:.2f} seconds!")


class Leaderboard:
    @staticmethod
    def record(rows: int, cols: int, time_sec: float, initials: str):
        key = f"{rows}x{cols}"
        data = {}
        if LEADERBOARD_FILE.exists():
            data = json.loads(LEADERBOARD_FILE.read_text())

        scores = data.get(key, [])
        scores.append({"initials": initials[:3], "time": time_sec})
        scores = sorted(scores, key=lambda x: x["time"])[:10]
        data[key] = scores

        LEADERBOARD_FILE.write_text(json.dumps(data, indent=2))


class SlidingPuzzleProgramUtils:
    pass


def _slice_image(img: tk.PhotoImage, rows: int, cols: int) -> tk.PhotoImage:
    return img


def _generate_image(rows: int, cols: int) -> tk.PhotoImage:
    size = 100 * cols, 100 * rows
    root = tk.Tk()
    root.withdraw()  # hide temporary root window
    img = tk.PhotoImage(width=size[0], height=size[1])
    for r in range(rows):
        for c in range(cols):
            color = f"#{random.randint(0, 0xFFFFFF):06x}"
            img.put(color, to=(c * 100, r * 100, (c + 1) * 100, (r + 1) * 100))
    return img


def _load_random_image() -> tk.PhotoImage | None:
    if not ASSETS_DIR.exists():
        return None
    images = [p for p in ASSETS_DIR.iterdir() if p.suffix.lower() in SUPPORTED_EXTENSIONS]
    if not images:
        return None
    return tk.PhotoImage(file=str(random.choice(images)))

class PuzzleSetupDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Rows (3-8):").grid(row=0, column=0, sticky="w")
        tk.Label(master, text="Columns (3-8):").grid(row=1, column=0, sticky="w")


        self.rows_var = tk.IntVar(value=4)
        self.cols_var = tk.IntVar(value=6)


        tk.Spinbox(master, from_=3, to=8, textvariable=self.rows_var).grid(row=0, column=1)
        tk.Spinbox(master, from_=3, to=8, textvariable=self.cols_var).grid(row=1, column=1)
        return master


    def apply(self):
        self.result = (self.rows_var.get(), self.cols_var.get())

def _prompt_grid_size():
    root = tk.Tk()
    root.withdraw()  # hide temporary root window

    dialog = PuzzleSetupDialog(root, title="Sliding Puzzle Setup")
    root.destroy()

    if dialog.result is None:
        raise SystemExit("Puzzle setup cancelled by user.")

    return dialog.result

SlidingPuzzleProgram._prompt_grid_size = staticmethod(_prompt_grid_size)

def _load_or_generate_image(rows: int, cols: int) -> tk.PhotoImage:
    img = _load_random_image()
    if img is None:
        return _generate_image(rows, cols)
    return img

SlidingPuzzleProgram._load_or_generate_image = staticmethod(_load_or_generate_image)