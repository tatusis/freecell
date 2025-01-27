from typing import cast

import cv2 as cv
import pygame

from ..config import Config
from ..easings import *
from ..subject import Subject
from .card_shadow import CardShadow
from .card_state import CardState
from .foundation_cell import FoundationCell
from .free_cell import FreeCell


class Card(pygame.sprite.Sprite, Subject):
    """Class that defines a card"""

    def __init__(self, suit: str, rank: str) -> None:
        """Instantiate a card"""
        pygame.sprite.Sprite.__init__(self)
        Subject.__init__(self)
        self.config = Config.instance().default
        self.suit = suit
        self.rank = rank
        self.suit_color = self.get_suit_color(self.suit)
        self.idx = 0
        self.column = 0
        self.row = 0
        self.cell = None
        self.previous_state = None
        self.state = CardState.dealer
        self.state_transition = True

        # Sounds
        self.drag_sound = pygame.mixer.Sound(f"assets/sounds/{self.config["card_drag_sound"]}")
        self.drop_sound = pygame.mixer.Sound(f"assets/sounds/{self.config["card_drop_sound"]}")

        # Sprites
        image_source = cv.imread(f"assets/sprites/card{suit}{rank}.png", cv.IMREAD_UNCHANGED)
        image = cv.cvtColor(image_source, cv.COLOR_BGRA2RGBA)
        image_resized = cv.resize(
            image,
            (self.config["card_width"], self.config["card_height"]),
            interpolation=cv.INTER_AREA,
        )
        self.default_image = pygame.image.frombytes(
            image_resized.tobytes(),
            (self.config["card_width"], self.config["card_height"]),
            "RGBA",
        ).convert_alpha()
        self.image = self.default_image.copy()
        self.rect = self.image.get_rect()

        # Initial position of all cards (dealer)
        self.rect.x = self.config["dealer_position_x"]
        self.rect.y = self.config["dealer_position_y"]

        self._layer = 0
        self._previous_layer = 0
        self.moving_time = 0
        self.shadow = CardShadow(self)
        self.drop_sound_play = True

    def get_suit_color(self, suit: str) -> str:
        """Returns the color of a suit"""
        match suit:
            case "Clubs":
                suit_color = "Black"
            case "Diamonds":
                suit_color = "Red"
            case "Hearts":
                suit_color = "Red"
            case "Spades":
                suit_color = "Black"

        return suit_color

    def get_default_pos(self) -> tuple[int, int]:
        """Returns the default position from the current state"""
        match self.state:
            case CardState.foundation_cell:
                default_pos = (
                    cast(FoundationCell, self.cell).rect.x,
                    cast(FoundationCell, self.cell).rect.y,
                )
            case CardState.free_cell:
                default_pos = (
                    cast(FreeCell, self.cell).rect.x,
                    cast(FreeCell, self.cell).rect.y,
                )
            case CardState.column_cell:
                default_pos = (
                    self.column * (self.rect.width + self.config["card_margin_x"]) + self.config["card_offset_x"],
                    self.row * round(self.rect.height * 0.235) + self.config["card_offset_y"],
                )
            case _:
                default_pos = (
                    self.rect.x,
                    self.rect.y,
                )

        return default_pos

    def add_minimal_border(self) -> None:
        """Adds a minimal border to a card"""
        pygame.draw.rect(
            self.image,
            self.config["card_minimal_border_color"],
            pygame.Rect(0, 0, self.config["card_width"], self.config["card_height"]),
            self.config["card_minimal_border_width"],
            self.config["card_minimal_border_radius"],
        )

    def add_highlighted_border(self) -> None:
        """Adds a highlighted border to a card"""
        pygame.draw.rect(
            self.image,
            self.config["card_highlighted_border_color"],
            pygame.Rect(0, 0, self.config["card_width"], self.config["card_height"]),
            self.config["card_highlighted_border_width"],
            self.config["card_highlighted_border_radius"],
        )

    def remove_border(self) -> None:
        """Remove highlighted border from a card"""
        self.image = self.default_image.copy()

    def drag(self, layer: int, mouse_x: int, mouse_y: int) -> None:
        """Pick up a card"""
        self.change_state(CardState.drag)
        self.remove_border()
        self.add_highlighted_border()
        self.set_state_transition(True)
        self.moving_time = 0
        self.dragging_offset_x = self.rect.x - mouse_x
        self.dragging_offset_y = self.rect.y - mouse_y
        self._previous_layer = self._layer
        self._layer = layer
        self.notify()

    def drop(
        self,
        state: CardState,
        is_valid_move: bool = False,
        moving_time: int = 0,
        drop_sound_play: bool = True,
    ) -> None:
        """Drop a card"""
        self.change_state(state)
        self.remove_border()
        self.add_minimal_border()
        self.set_state_transition(True)
        self.set_moving_time(moving_time)
        self.drop_sound_play = drop_sound_play

        if not is_valid_move:
            self._layer = self._previous_layer

    def set_moving_time(self, moving_time: float) -> None:
        """Sets the default timing in the animation"""
        self.moving_time = moving_time
        self.shadow.moving_time = moving_time

    def set_state_transition(self, state: bool, only_shadow: bool = False) -> None:
        """Defines whether the card and/or shadow are in state transition"""
        if not only_shadow:
            self.state_transition = state

        self.shadow.state_transition = state

    def change_state(self, next_state: CardState) -> None:
        """Changes the state of the card and its shadow"""
        self.previous_state = self.state
        self.state = next_state

    def process_transition(self, dt: float, duration: float, easing: callable = ease_out_quart) -> None:
        """Processes animation when transitioning between states"""
        end_x, end_y = self.get_default_pos()
        interval_x, interval_y = (end_x - self.rect.x), (end_y - self.rect.y)

        if abs(interval_x) <= 2 and abs(interval_y) <= 2:
            self.moving_time = 0
            self.rect.x, self.rect.y = self.get_default_pos()
            self.state_transition = False
            self.notify()
        else:
            self.moving_time += dt

            if self.moving_time >= 0:
                self.rect.x += round(interval_x * easing(self.moving_time / duration))
                self.rect.y += round(interval_y * easing(self.moving_time / duration))

    def update(self, dt: float) -> None:
        """Processes the sprite update"""
        if self.state_transition:
            match self.state:
                case CardState.column_cell:
                    if self.previous_state == CardState.dealer:
                        self.process_transition(dt, self.config["card_moving_time"])
                    elif self.previous_state == CardState.drag:
                        self.process_transition(dt, self.config["card_moving_time"])

                case CardState.free_cell:
                    if self.previous_state == CardState.drag:
                        self.process_transition(dt, self.config["card_moving_time"])

                case CardState.foundation_cell:
                    if self.previous_state == CardState.drag:
                        self.process_transition(dt, self.config["card_moving_time"])

            if not self.state_transition:
                if self.previous_state != CardState.dealer:
                    if self.drop_sound_play:
                        self.drop_sound.play()

        match self.state:
            case CardState.drag:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.rect.x = mouse_x + self.dragging_offset_x
                self.rect.y = mouse_y + self.dragging_offset_y
