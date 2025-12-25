# -*- coding: utf-8 -*-
# programs/PySlidingPuzzle.py

"""
Sliding Puzzle Game

- Auto-discovered by main menu
- Uses tkinter for UI
- Supports size-specific image puzzles
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
from typing import Tuple, Optional
import tkinter as tk
from tkinter import simpledialog, messagebox

from PyProgramBase import ProgramBase

ASSETS_DIR = Path("assets/SlidingPuzzleImages")
LEADERBOARD_FILE = Path("sliding_puzzle_leaderboard.json")
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}


class SlidingPuzzleProgram(ProgramBase):
    @staticmethod
    def _prompt_grid_size() -> Tuple[int, int]:
        """Prompt user for grid size"""
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        dialog = PuzzleSetupDialog(root, title="Sliding Puzzle Setup")
        root.destroy()

        if dialog.result is None:
            raise SystemExit("Puzzle setup cancelled by user.")

        return dialog.result

    @staticmethod
    def _get_size_specific_image_path(rows: int, cols: int) -> Optional[Path]:
        """
        Get the image path for the specific grid size.
        Looks for files named like: puzzle_3x3.png, puzzle_4x5.jpg, etc.
        """
        if not ASSETS_DIR.exists():
            return None
        
        # First, try exact dimension match with various extensions
        base_name = f"puzzle_{rows}x{cols}"
        
        for ext in SUPPORTED_EXTENSIONS:
            # Try both lowercase and uppercase extensions
            image_path = ASSETS_DIR / f"{base_name}{ext}"
            if image_path.exists():
                return image_path
            
            image_path = ASSETS_DIR / f"{base_name}{ext.upper()}"
            if image_path.exists():
                return image_path
        
        # If no exact match, try to find any image that starts with the dimension
        # This allows for variations like puzzle_3x3_v1.png, puzzle_3x3_landscape.jpg
        pattern = f"{base_name}*"
        matching_files = []
        
        for ext in SUPPORTED_EXTENSIONS:
            matching_files.extend(ASSETS_DIR.glob(f"{pattern}{ext}"))
            matching_files.extend(ASSETS_DIR.glob(f"{pattern}{ext.upper()}"))
        
        if matching_files:
            return matching_files[0]  # Return first match
        
        return None

    def run(self):
        rows, cols = self._prompt_grid_size()
        
        # Get the size-specific image
        image_path = self._get_size_specific_image_path(rows, cols)
        if image_path is None:
            # Create a temporary root for the error dialog
            root = tk.Tk()
            root.withdraw()
            
            # Suggest available images if none found for this size
            available_sizes = self._get_available_sizes()
            if available_sizes:
                sizes_text = "\n".join([f"  {size}" for size in available_sizes])
                error_msg = (
                    f"No image found for {rows}x{cols} puzzle.\n\n"
                    f"Please add an image named 'puzzle_{rows}x{cols}.png' to:\n"
                    f"{ASSETS_DIR}\n\n"
                    f"Available puzzle sizes:\n{sizes_text}"
                )
            else:
                error_msg = (
                    f"No puzzle images found.\n\n"
                    f"Please add images to:\n{ASSETS_DIR}\n"
                    f"Named like: puzzle_3x3.png, puzzle_4x4.jpg, etc."
                )
            
            messagebox.showerror("Image Not Found", error_msg)
            root.destroy()
            return
            
        # Start the game with the size-specific image
        game = SlidingPuzzleGame(rows, cols, image_path)
        game.start()

    @staticmethod
    def _get_available_sizes() -> list[str]:
        """Get list of available puzzle sizes from image filenames"""
        if not ASSETS_DIR.exists():
            return []
        
        sizes = set()
        for ext in SUPPORTED_EXTENSIONS:
            # Look for files with pattern puzzle_ROWSxCOLS.ext
            for file_path in ASSETS_DIR.glob(f"puzzle_*x*{ext}"):
                for file_path_upper in ASSETS_DIR.glob(f"puzzle_*x*{ext.upper()}"):
                    pass
                
                # Extract dimensions from filename
                stem = file_path.stem  # Gets filename without extension
                if stem.startswith("puzzle_"):
                    dim_part = stem[7:]  # Remove "puzzle_" prefix
                    if "x" in dim_part:
                        # Take only the dimension part (ignore any additional suffixes)
                        dim_part = dim_part.split("_")[0]  # Gets "3x3" from "3x3_v1"
                        sizes.add(dim_part)
        
        return sorted(list(sizes), key=lambda x: tuple(map(int, x.split('x'))))


class SlidingPuzzleGame:
    TILE_SIZE = 100  # Each tile will be 100x100 pixels

    def __init__(self, rows: int, cols: int, image_path: Path):
        self.rows = rows
        self.cols = cols
        self.image_path = image_path

        self.root = tk.Tk()
        self.root.title(f"Sliding Puzzle - {rows}x{cols}")

        # Load the size-specific image
        try:
            self.image = tk.PhotoImage(file=str(image_path))
            self._validate_image_size()
        except Exception as e:
            messagebox.showerror(
                "Image Error",
                f"Failed to load image: {e}\n\n"
                f"Path: {image_path}\n"
                f"Expected size: {cols * self.TILE_SIZE}x{rows * self.TILE_SIZE}"
            )
            self.root.destroy()
            raise
        
        # Store tile images
        self.tile_images = self._create_tile_images()

        # Set window size based on image dimensions
        window_width = self.image.width()
        window_height = self.image.height()
        
        self.canvas = tk.Canvas(
            self.root,
            width=window_width,
            height=window_height,
        )
        self.canvas.pack()

        self.start_time: Optional[float] = None
        self.solved = False

        self.tiles, self.empty_pos = self._create_tiles()
        self._shuffle_tiles()
        self._draw()

        self.canvas.bind("<Button-1>", self._on_click)
        self.root.bind("<Key>", self._on_key)

    def _validate_image_size(self):
        """Check that the image matches the expected puzzle size"""
        actual_width = self.image.width()
        actual_height = self.image.height()
        
        expected_width = self.cols * self.TILE_SIZE
        expected_height = self.rows * self.TILE_SIZE
        
        if actual_width != expected_width or actual_height != expected_height:
            # Warn but continue - the image might still work
            print(f"Warning: Image size mismatch. "
                  f"Expected: {expected_width}x{expected_height}, "
                  f"Actual: {actual_width}x{actual_height}")
            
            new_tile_width = actual_width // self.cols
            new_tile_height = actual_height // self.rows
            
            if new_tile_width == new_tile_height and new_tile_width > 0:
                self.TILE_SIZE = new_tile_width
                print(f"Adjusted tile size to: {self.TILE_SIZE}")
            else:
                # Images must be evenly divisible by grid dimensions
                messagebox.showwarning(
                    "Image Size Warning",
                    f"Image dimensions ({actual_width}x{actual_height}) are not "
                    f"evenly divisible by grid size ({self.cols}x{self.rows}).\n"
                    f"Some tiles may not display correctly."
                )

    def start(self):
        self.root.mainloop()
        
    def _create_tile_images(self):
        """Create individual PhotoImage objects for each tile"""
        tile_images = {}
        for r in range(self.rows):
            for c in range(self.cols):
                # Calculate tile boundaries
                x1 = c * self.TILE_SIZE
                y1 = r * self.TILE_SIZE
                x2 = (c + 1) * self.TILE_SIZE
                y2 = (r + 1) * self.TILE_SIZE
                
                # Create a new PhotoImage with just the tile portion
                tile_img = tk.PhotoImage()
                tile_img.tk.call(
                    tile_img, 'copy', self.image, 
                    '-from', x1, y1, x2, y2,
                    '-to', 0, 0
                )
                tile_images[(r, c)] = tile_img
        return tile_images

    def _create_tiles(self):
        tiles = []
        for r in range(self.rows):
            for c in range(self.cols):
                if r == self.rows - 1 and c == self.cols - 1:
                    tiles.append(None)  # Empty space at bottom-right
                else:
                    tiles.append((r, c))
        return tiles, (self.rows - 1, self.cols - 1)

    def _shuffle_tiles(self):
        # # Fisher-Yates shuffle for movable tiles (removed)
        # movable_indices = [i for i, t in enumerate(self.tiles) if t is not None]
        
        # for i in range(len(movable_indices) - 1, 0, -1):
            # j = random.randint(0, i)
            # idx_i = movable_indices[i]
            # idx_j = movable_indices[j]
            # self.tiles[idx_i], self.tiles[idx_j] = self.tiles[idx_j], self.tiles[idx_i]

        # First, generate the puzzle in a solved state
        solved_tiles = []
        for r in range(self.rows):
            for c in range(self.cols):
                if r == self.rows - 1 and c == self.cols - 1:
                    solved_tiles.append(None)
                else:
                    solved_tiles.append((r, c))
        # Perform a large number of random moves from the solved state
        # This ensures the puzzle can be solvable
        empty_pos = (self.rows - 1, self.cols - 1)
        num_moves = self.rows * self.cols * (self.rows + self.cols)^2

        for _ in range(num_moves):
            # Find all possible moves from the current empty space
            er, ec = empty_pos
            possible_moves = []

            if er > 0: # there is a tile below the empty tile
                possible_moves.append((er - 1, ec))
            if er < self.rows - 1: # there is a tile above the empty tile
                possible_moves.append((er + 1, ec))
            if ec > 0: # there is a tile right of the empty tile
                possible_moves.append((er, ec - 1))
            if ec < self.cols - 1: # there is a tile left of the empty tile
                possible_moves.append((er, ec + 1))

            # choose a random move
            if possible_moves:
                move_r, move_c = random.choice(possible_moves)

                # make a move
                move_idx = move_r * self.cols + move_c
                empty_idx = er * self.cols + ec
                self.tiles[empty_idx], self.tiles[move_idx] = (
                    self.tiles[move_idx],
                    None,
                )
                # Update empty position
                empty_pos = (move_r, move_c)
        
        # Update self.empty_pos to match the final empty position
        self.empty_pos = empty_pos

    def _draw(self):
        self.canvas.delete("all")
        for idx, tile in enumerate(self.tiles):
            r, c = divmod(idx, self.cols)
            x0 = c * self.TILE_SIZE
            y0 = r * self.TILE_SIZE

            if tile is None:
                # Draw empty tile (background color)
                self.canvas.create_rectangle(
                    x0, y0, 
                    x0 + self.TILE_SIZE, y0 + self.TILE_SIZE,
                    fill="gray", outline="black"
                )
                continue

            tr, tc = tile
            # Draw the tile image
            self.canvas.create_image(
                x0 + self.TILE_SIZE // 2,
                y0 + self.TILE_SIZE // 2,
                image=self.tile_images[(tr, tc)],
                anchor="center"
            )
            
            # Draw tile border
            self.canvas.create_rectangle(
                x0, y0, 
                x0 + self.TILE_SIZE, y0 + self.TILE_SIZE,
                outline="black"
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
                # Check if this is the correct position for the empty tile
                expected_r, expected_c = divmod(idx, self.cols)
                if not (expected_r == self.rows - 1 and expected_c == self.cols - 1):
                    return False
                continue
            if tile != divmod(idx, self.cols):
                return False
        return True

    def _on_solved(self):
        self.solved = True
        elapsed = time.time() - self.start_time
        initials = simpledialog.askstring(
            "Solved!", 
            f"Time: {elapsed:.2f}s\nEnter initials (3 chars max):"
        )
        if initials:
            Leaderboard.record(self.rows, self.cols, elapsed, initials[:3])
        messagebox.showinfo("Completed", f"Puzzle solved in {elapsed:.2f} seconds!")
        self.root.destroy()


class Leaderboard:
    @staticmethod
    def record(rows: int, cols: int, time_sec: float, initials: str):
        key = f"{rows}x{cols}"
        data = {}
        if LEADERBOARD_FILE.exists():
            try:
                data = json.loads(LEADERBOARD_FILE.read_text())
            except json.JSONDecodeError:
                data = {}

        scores = data.get(key, [])
        scores.append({"initials": initials, "time": round(time_sec, 2)})
        scores = sorted(scores, key=lambda x: x["time"])[:10]
        data[key] = scores

        LEADERBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
        LEADERBOARD_FILE.write_text(json.dumps(data, indent=2))


class PuzzleSetupDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Rows (3-8):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(master, text="Columns (3-8):").grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.rows_var = tk.IntVar(value=4)
        self.cols_var = tk.IntVar(value=4)

        tk.Spinbox(
            master, from_=3, to=8, textvariable=self.rows_var, width=10
        ).grid(row=0, column=1, padx=5, pady=5)
        tk.Spinbox(
            master, from_=3, to=8, textvariable=self.cols_var, width=10
        ).grid(row=1, column=1, padx=5, pady=5)
        
        return master

    def validate(self):
        rows = self.rows_var.get()
        cols = self.cols_var.get()
        if 3 <= rows <= 8 and 3 <= cols <= 8:
            return True
        messagebox.showerror("Error", "Rows and columns must be between 3 and 8")
        return False

    def apply(self):
        self.result = (self.rows_var.get(), self.cols_var.get())