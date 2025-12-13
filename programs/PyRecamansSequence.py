# programs/PyRecamansSequence.py

from PyProgramBase import ProgramBase

class RecamansSequence(ProgramBase):

    """Generate and display the first 100 values of Recaman's sequence."""

    MAX_TERMS = 1000

    def run(self):
        print("Recaman's Sequence (first 1000 terms)\n")
        print("""
            The sequence uses the following rules.../n
            1. a(n) = a(n−1) − n if the result is positive AND not already in the sequence/n
            otherwise: /n
            2. a(n) = a(n−1) + n /n
        """)

        current = 0
        seen = {current}

        print(f"a(0) = {current}")

        # why: sequence rules require uniqueness and positivity checks
        for n in range(1, self.MAX_TERMS):
            candidate = current - n

            if candidate > 0 and candidate not in seen:
                current = candidate
            else:
                current = current + n

            seen.add(current)
            print(f"a({n}) = {current}")
