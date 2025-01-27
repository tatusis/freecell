from abc import ABC, abstractmethod

from .subject import Subject


class Observer(ABC):
    """Class that defines an observer"""

    @abstractmethod
    def update(self, subject: Subject) -> None:
        """Processes the update of the observed object"""
        pass
