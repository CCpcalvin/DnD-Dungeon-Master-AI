class Progression:
    def __init__(self, end: int):
        self.completion_rate: int = 0
        self.end = end

    def fail(self):
        """Set the progression to fail."""
        self.completion_rate = -1

    def progress(self):
        """Increment the progression by a specified amount."""
        self.completion_rate += 1

        if self.completion_rate > self.end:
            self.completion_rate = self.end

    def is_failed(self) -> bool:
        """Check if the progression has failed."""
        return self.completion_rate == -1

    def is_completed(self) -> bool:
        """Check if the progression is complete."""
        return self.completion_rate == self.end

    def to_prompt(self) -> str:
        """Convert the progression to a string for prompt."""
        if self.is_failed():
            return "Fail"

        if self.is_completed():
            return "Complete"

        return f"{self.completion_rate}/{self.end}"
