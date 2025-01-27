from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .observer import Observer


class Subject(ABC):
    """Class that defines an observed object"""

    def __init__(self):
        """Instantiate an observed object"""
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        """Attaches an observer to the object"""
        self._observers.append(observer)

    def notify(self) -> None:
        """Notifies the observer about an update to the object"""
        for observer in self._observers:
            observer.update(self)
