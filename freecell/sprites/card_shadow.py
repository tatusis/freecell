from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import pygame

from ..config import Config
from ..easings import *
from .card_state import CardState

if TYPE_CHECKING:
    from .card import Card


class CardShadow(pygame.sprite.Sprite):
    """Class that defines the shadow of a card"""

    def __init__(self, card: Card) -> None:
        """Instantiate a card's shadow"""
        super().__init__()
        self.config = Config.instance().default

        self.card = card
        self.state_transition = True

        # Sprites
        self.image = pygame.Surface((self.config["card_width"], self.config["card_height"]), pygame.SRCALPHA)
        pygame.draw.rect(
            self.image,
            self.config["shadow_color"],
            pygame.Rect(
                self.config["shadow_border_width"],
                self.config["shadow_border_width"],
                self.config["card_width"] - (2 * self.config["shadow_border_width"]),
                self.config["card_height"] - (2 * self.config["shadow_border_width"]),
            ),
        )
        pygame.draw.rect(
            self.image,
            self.config["shadow_color"],
            pygame.Rect(0, 0, self.config["card_width"], self.config["card_height"]),
            self.config["shadow_border_width"],
            self.config["shadow_border_radius"],
        )
        self.image.set_alpha(self.config["shadow_alpha"])
        self.rect = self.image.get_rect()

        # Initial position of all cards (dealer)
        self.rect.x = self.config["dealer_position_x"] + self.config["shadow_offset"]
        self.rect.y = self.config["dealer_position_y"] + self.config["shadow_offset"]

        self._layer = 0
        self.moving_time = 0

    def get_default_pos(self) -> tuple[int, int]:
        """Returns the default position from the current state"""
        card_default_pos = self.card.get_default_pos()

        match self.card.state:
            case CardState.drag:
                default_pos = (
                    card_default_pos[0] + self.config["moving_shadow_offset"],
                    card_default_pos[1] + self.config["moving_shadow_offset"],
                )
            case _:
                default_pos = (
                    card_default_pos[0] + self.config["shadow_offset"],
                    card_default_pos[1] + self.config["shadow_offset"],
                )

        return default_pos

    def process_transition(self, dt: float, duration: float, easing: Callable = ease_out_quart) -> None:
        """Processes animation when transitioning between states"""
        begin_x, begin_y = self.rect.x, self.rect.y
        end_x, end_y = self.get_default_pos()
        interval_x = end_x - begin_x
        interval_y = end_y - begin_y

        if abs(interval_x) <= 2 and abs(interval_y) <= 2:
            self.moving_time = 0
            self.rect.x, self.rect.y = self.get_default_pos()
            self.state_transition = False
        else:
            self.moving_time += dt

            if self.moving_time >= 0:
                self.rect.x += round(interval_x * easing(self.moving_time / duration))
                self.rect.y += round(interval_y * easing(self.moving_time / duration))

    def update(self, dt: float) -> None:
        """Processes the sprite update"""
        if self.state_transition:
            match self.card.state:
                case CardState.foundation_cell:
                    if self.card.previous_state == CardState.drag:
                        self.process_transition(dt, self.config["card_moving_time"])

                case CardState.free_cell:
                    if self.card.previous_state == CardState.drag:
                        self.process_transition(dt, self.config["card_moving_time"])

                case CardState.column_cell:
                    if self.card.previous_state == CardState.dealer:
                        self.process_transition(dt, self.config["card_moving_time"])
                    elif self.card.previous_state == CardState.drag:
                        self.process_transition(dt, self.config["card_moving_time"])

                case CardState.drag:
                    self.process_transition(dt, self.config["card_moving_time"])

        match self.card.state:
            case CardState.drag:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.rect.x = mouse_x + self.card.dragging_offset_x + self.config["moving_shadow_offset"]
                self.rect.y = mouse_y + self.card.dragging_offset_y + self.config["moving_shadow_offset"]
