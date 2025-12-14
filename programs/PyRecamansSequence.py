# programs/PyRecamansSequence.py

from PyProgramBase import ProgramBase
import json
from pathlib import Path


class RecamansSequence(ProgramBase):

    """
    Generate Recaman's sequence with persistent storage.

    Amendments:
    - Entire sequence is stored across runs
    - Duplicates are prevented using stored history
    - 100 new values are appended per execution
    - Storage file size is monitored (10 MB limit)
    """

    # ORIGINAL CONSTANT (no longer used)
    # MAX_TERMS = 1000

    # NEW CONSTANTS
    APPEND_COUNT = 1000
    MAX_FILE_SIZE_MB = 100
    STORAGE_FILE = Path("recaman_sequence.json")

    def run(self):
        print("Recaman's Sequence (persistent mode)\n")
        print("""
            The sequence uses the following rules.../n
            1. a(n) = a(n−1) − n if the result is positive AND not already in the sequence/n
            otherwise: /n
            2. a(n) = a(n−1) + n /n
        """)

        # --- NEW: check storage file size before loading ---
        if self._storage_exceeds_limit():
            if self._prompt_delete_storage():
                self._delete_storage()
                print("Sequence file deleted. Next run will start fresh.\n")
                return

        # --- NEW: load full historical sequence ---
        sequence = self._load_sequence()

        start_index = len(sequence)

        # ------------------------------------------------------------------
        # ORIGINAL IMPLEMENTATION (kept for reference, now disabled)
        # ------------------------------------------------------------------
        #
        # current = 0
        # seen = {current}
        # 
        # print(f"a(0) = {current}")
        # 
        # why: sequence rules require uniqueness and positivity checks
        # for n in range(1, self.MAX_TERMS):
        #     candidate = current - n
        # 
        #     if candidate > 0 and candidate not in seen:
        #         current = candidate
        #     else:
        #         current = current + n
        # 
        #     seen.add(current)
        #     print(f"a({n}) = {current}")
        #
        # ------------------------------------------------------------------

        # --- NEW: append 1000 new values per execution ---
        for _ in range(self.APPEND_COUNT):
            next_value = self._compute_next(sequence)
            sequence.append(next_value)

        self._save_sequence(sequence)

        end_index = len(sequence) - 1
        print(f"Added {self.APPEND_COUNT} new values.")
        print(f"Sequence range: a({start_index}) → a({end_index})")
        print(f"Latest value: {sequence[-1]}")

    # =========================
    # NEW HELPER METHODS
    # =========================

    def _load_sequence(self):
        # why: full history is required to prevent duplicates across runs
        if self.STORAGE_FILE.exists():
            with self.STORAGE_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        return [0]

    def _save_sequence(self, sequence):
        # why: persist state so future runs remain mathematically valid
        with self.STORAGE_FILE.open("w", encoding="utf-8") as f:
            json.dump(sequence, f)

    def _compute_next(self, sequence):
        # why: Recamán rule depends on entire sequence history
        current = sequence[-1]
        n = len(sequence)
        seen = set(sequence)

        candidate = current - n
        if candidate > 0 and candidate not in seen:
            return candidate

        return current + n

    def _storage_exceeds_limit(self):
        if not self.STORAGE_FILE.exists():
            return False

        size_mb = self.STORAGE_FILE.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            print(
                f"Storage file size: {size_mb:.2f} MB "
                f"(limit: {self.MAX_FILE_SIZE_MB} MB)"
            )
            return True

        return False

    def _prompt_delete_storage(self):
        # why: user must explicitly approve destructive reset
        while True:
            choice = input(
                "Delete sequence file and restart on next run? (y/n): "
            ).strip().lower()
            if choice in {"y", "n"}:
                return choice == "y"

    def _delete_storage(self):
        self.STORAGE_FILE.unlink(missing_ok=True)

