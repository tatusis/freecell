from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from ..game import Game


class Scene(ABC):
    """Class that defines a scene"""

    def __init__(self, game: Game):
        """Instantiate a scene"""
        super().__init__()
        self.game = game

    @abstractmethod
    def ready(self) -> None:
        """Set the scene for execution"""
        pass

    @abstractmethod
    def process_events(self, event: pygame.event.Event) -> None:
        """Processes input events"""
        pass

    @abstractmethod
    def process_update(self, dt: float) -> None:
        """Processes the sprite update"""
        pass

    @abstractmethod
    def process_draw(self) -> None:
        """Renders the frames of the scene"""
        pass
