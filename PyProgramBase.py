# PyProgramBase.py

class ProgramBase:
    """Base class all programs must extend."""
    def run(self):
        raise NotImplementedError("Subclasses must implement run().")
