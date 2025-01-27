from abc import ABC, abstractmethod


class Cell(ABC):
    """Class that defines a cell"""

    def __init__(self):
        """Instantiate a cell"""
        super().__init__()
        self.highlighted = False

    @abstractmethod
    def add_highlight(self) -> None:
        """Adds highlight to a cell"""
        pass

    @abstractmethod
    def remove_highlight(self) -> None:
        """Remove highlight from a cell"""
        pass
