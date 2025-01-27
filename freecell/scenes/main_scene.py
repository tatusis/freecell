from __future__ import annotations

import math
import random
import time
from typing import TYPE_CHECKING, cast

import pygame

from ..config import Config
from ..dealer import Dealer
from ..deck import Deck
from ..observer import Observer
from ..sprites.card import Card, CardState
from ..sprites.cell import Cell
from ..sprites.column_cell import ColumnCell
from ..sprites.foundation_cell import FoundationCell
from ..sprites.free_cell import FreeCell
from ..sprites.mouse import Mouse
from .scene import Scene

if TYPE_CHECKING:
    from ..game import Game


class MainScene(Scene, Observer):
    """Class that defines the main scene"""

    def __init__(self, game: Game) -> None:
        """Instantiate the main scene"""
        Scene.__init__(self, game)
        Observer.__init__(self)
        self.config = Config.instance().default

        # State
        self.seed = None
        self.is_dragging_card = None
        self.card_being_dragged = None
        self.other_cards_being_dragged: list[Card] = []

        # Deck
        self.deck = None

        # Dealer
        self.dealer = None

        # Sprites
        self.mouse_sprite = None
        self.all_sprites = None
        self.card_sprites = None
        self.cell_sprites = None
        self.click_time = 0

        # Music
        pygame.mixer.music.load(f"assets/sounds/{self.config["background_music"]}")

        # Sounds
        self.sound_channel = None
        self.loading_sound = pygame.mixer.Sound(f"assets/sounds/{self.config["loading_sound"]}")
        self.start_sound = pygame.mixer.Sound(f"assets/sounds/{self.config["start_sound"]}")

        self.default_font = pygame.font.Font(
            f"assets/fonts/{self.config["default_font"]}",
            20,
        )

        # Texts
        self.texts = {}
        self.texts["menu"] = self.prepare_text(
            self.default_font,
            self.config["menu_text"],
            self.config["default_font_color"],
            0.10,
        )
        self.texts["new_game"] = self.prepare_text(
            self.default_font,
            self.config["new_game_text"],
            self.config["default_font_color"],
            0.20,
        )
        self.texts["same_game"] = self.prepare_text(
            self.default_font,
            self.config["restart_text"],
            self.config["default_font_color"],
            0.25,
        )

    # Default methods

    def ready(self, new_game: bool = True) -> None:
        """Set the scene for execution"""
        self.sound_channel = pygame.mixer.find_channel()
        self.sound_channel.queue(self.loading_sound)
        self.sound_channel.queue(self.start_sound)
        pygame.mixer.music.play(-1, fade_ms=10000)

        # State
        self.is_dragging_card = False
        self.card_being_dragged = None

        # Deck
        self.deck = Deck()

        if new_game:
            self.seed = time.time()

        random.seed(self.seed)
        self.deck.shuffle()

        # Dealer
        self.dealer = Dealer(self.deck)
        self.dealer.prepare_table()
        self.dealer.deal()

        # Sprites
        self.mouse_sprite = Mouse()
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.card_sprites = pygame.sprite.Group()
        self.cell_sprites = pygame.sprite.Group()

        # Foundation cell sprites
        for foundation_cell in self.dealer.foundation_cells:
            self.cell_sprites.add(foundation_cell)
            self.all_sprites.add(foundation_cell)

        # Free cell sprites
        for free_cell in self.dealer.free_cells:
            self.cell_sprites.add(free_cell)
            self.all_sprites.add(free_cell)

        # Column cell sprites
        for column_cell in self.dealer.column_cells:
            self.cell_sprites.add(column_cell)
            self.all_sprites.add(column_cell)

        # Card sprites
        for card in self.deck.cards:
            card.attach(self)
            self.card_sprites.add(card)
            self.all_sprites.add(card)
            self.all_sprites.add(card.shadow)

    def process_events(self, event: pygame.event.Event) -> None:
        """Processes input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                self.sound_channel.stop()
                pygame.mixer.music.stop()
                self.ready()

            if event.key == pygame.K_r:
                self.sound_channel.stop()
                pygame.mixer.music.stop()
                self.ready(False)

            if event.key == pygame.K_BACKSPACE:
                self.game.change_scene("MenuScene")

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if time.time() - self.click_time < 0.3:
                    self.fast_foundation_cell_drop_card()
                else:
                    self.drag_card()

                self.click_time = time.time()

        if event.type == pygame.MOUSEMOTION:
            self.check_card_cell_collision()

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.drop_card()

    def process_update(self, dt: float) -> None:
        """Processes the sprite update"""
        self.all_sprites.update(dt=dt)

    def process_draw(self) -> None:
        """Renders game frames"""
        for text in self.texts.values():
            self.game.screen.blit(text[0], text[1])

        self.all_sprites.draw(self.game.screen)

    def update(self, card: Card) -> None:
        """Updates the observer"""
        self.all_sprites.change_layer(card, card._layer)
        self.all_sprites.change_layer(card.shadow, card._layer - 1)

    # Local methods

    def update_mouse_sprite(self, return_coordinates: bool = False) -> tuple[int, int] | None:
        """Updates mouse sprite"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.mouse_sprite.rect.x = mouse_x
        self.mouse_sprite.rect.y = mouse_y

        if return_coordinates:
            return (mouse_x, mouse_y)
        else:
            return

    def drag_card(self) -> None:
        """Try to pick up a card from the table"""
        if not self.is_dragging_card:
            mouse_x, mouse_y = self.update_mouse_sprite(True)

            card_sprites: list[Card] = pygame.sprite.spritecollide(self.mouse_sprite, self.card_sprites, False)
            card_sprites.sort(key=lambda x: x.row)

            if len(card_sprites) > 0:
                card_sprite = card_sprites[-1]
                can_drag, cards_list = self.dealer.can_drag(card_sprite)

                if can_drag:
                    if cards_list is not None:
                        self.is_dragging_card = True
                        self.card_being_dragged = cards_list[0]
                        self.card_being_dragged.drag_sound.play()
                        self.other_cards_being_dragged = cards_list[1:]

                        for card in cards_list:
                            card.drag(self.config["card_being_dragged_layer"], mouse_x, mouse_y)
                    else:
                        self.is_dragging_card = True
                        self.card_being_dragged = card_sprite
                        self.card_being_dragged.drag_sound.play()
                        self.card_being_dragged.drag(self.config["card_being_dragged_layer"], mouse_x, mouse_y)

    def get_closest_cell_sprite(self, cell_sprites) -> Cell:
        """Returns the cell closest to the card"""
        sprites_distances = dict()

        for cell_sprite in cell_sprites:
            distance = math.dist(self.card_being_dragged.rect.center, cell_sprite.rect.center)
            sprites_distances[cell_sprite] = distance

        return min(sprites_distances.items(), key=lambda x: x[1])[0]

    def fast_foundation_cell_drop_card(self) -> None:
        """Allows for quick sending of valid cards to the foundation cells"""
        pass

    def drop_card(self) -> None:
        """Try to put a card down on the table"""
        if self.is_dragging_card:
            is_valid_move = False

            # Cell Sprites
            cell_sprites: list[Cell] = pygame.sprite.spritecollide(
                self.card_being_dragged,
                self.cell_sprites,
                False,
            )
            cell_sprites_count = len(cell_sprites)

            if cell_sprites_count > 0:
                if cell_sprites_count == 1:
                    closest_cell_sprite = cell_sprites[0]
                else:
                    closest_cell_sprite = self.get_closest_cell_sprite(cell_sprites)

                if isinstance(closest_cell_sprite, FoundationCell):
                    if len(self.other_cards_being_dragged) == 0:
                        if self.dealer.can_drop_foundation_cell(self.card_being_dragged, closest_cell_sprite):
                            previous_cell = self.card_being_dragged.cell

                            if self.card_being_dragged.previous_state == CardState.column_cell:
                                self.dealer.remove_card_column_cell(self.card_being_dragged)
                            elif self.card_being_dragged.previous_state == CardState.free_cell:
                                self.dealer.remove_card_free_cell(self.card_being_dragged, previous_cell)

                            self.dealer.add_card_foundation_cell(self.card_being_dragged, closest_cell_sprite)
                            self.card_being_dragged.drop(CardState.foundation_cell, True)
                            is_valid_move = True

                elif isinstance(closest_cell_sprite, FreeCell):
                    if len(self.other_cards_being_dragged) == 0:
                        if self.dealer.can_drop_free_cell(closest_cell_sprite):
                            previous_cell = self.card_being_dragged.cell

                            if self.card_being_dragged.previous_state == CardState.column_cell:
                                self.dealer.remove_card_column_cell(self.card_being_dragged)
                            elif self.card_being_dragged.previous_state == CardState.free_cell:
                                self.dealer.remove_card_free_cell(self.card_being_dragged, previous_cell)

                            self.dealer.add_card_free_cell(self.card_being_dragged, closest_cell_sprite)
                            self.card_being_dragged.drop(CardState.free_cell, True)
                            is_valid_move = True

                elif isinstance(closest_cell_sprite, ColumnCell):
                    if self.dealer.can_drop_column_cell(
                        self.card_being_dragged, closest_cell_sprite, self.other_cards_being_dragged
                    ):
                        previous_cell = self.card_being_dragged.cell

                        if self.card_being_dragged.previous_state == CardState.column_cell:
                            self.dealer.remove_card_column_cell(self.card_being_dragged)

                            if len(self.other_cards_being_dragged) > 0:

                                for card_being_dragged in self.other_cards_being_dragged:
                                    self.dealer.remove_card_column_cell(card_being_dragged)

                        elif self.card_being_dragged.previous_state == CardState.free_cell:
                            self.dealer.remove_card_free_cell(self.card_being_dragged, previous_cell)

                        self.dealer.add_card_column_cell(self.card_being_dragged, closest_cell_sprite)
                        self.card_being_dragged.drop(CardState.column_cell, True)

                        if len(self.other_cards_being_dragged) > 0:
                            idx = 1
                            for card_being_dragged in self.other_cards_being_dragged:
                                self.dealer.add_card_column_cell(card_being_dragged, closest_cell_sprite)
                                card_being_dragged.drop(CardState.column_cell, True, -idx / 25, False)
                                idx += 1

                        is_valid_move = True

            if not is_valid_move:
                self.card_being_dragged.drop(self.card_being_dragged.previous_state)

                if len(self.other_cards_being_dragged) > 0:
                    idx = 1
                    for card_being_dragged in self.other_cards_being_dragged:
                        card_being_dragged.drop(
                            card_being_dragged.previous_state,
                            moving_time=-idx / 25,
                            drop_sound_play=False,
                        )
                        idx += 1

            self.is_dragging_card = False
            self.card_being_dragged = None
            self.other_cards_being_dragged = []
            self.remove_cell_sprites_highlight()

    def check_card_cell_collision(self) -> None:
        """Checks collision of card with cells"""
        if self.is_dragging_card:
            self.update_mouse_sprite(False)

            cell_sprites: list[Cell] = pygame.sprite.spritecollide(
                self.card_being_dragged,
                self.cell_sprites,
                False,
            )
            cell_sprites_count = len(cell_sprites)

            if cell_sprites_count > 0:
                if cell_sprites_count == 1:
                    closest_cell_sprite = cell_sprites[0]
                else:
                    closest_cell_sprite = self.get_closest_cell_sprite(cell_sprites)

                closest_cell_sprite.add_highlight()
                self.remove_cell_sprites_highlight(closest_cell_sprite)
            else:
                self.remove_cell_sprites_highlight()

    def remove_cell_sprites_highlight(self, closest_cell_sprite: Cell = None) -> None:
        """Remove highlight from all cells"""
        cell_sprites_typed = cast(list[Cell], self.cell_sprites.sprites())

        if closest_cell_sprite is not None:
            for cell_sprite in cell_sprites_typed:
                if cell_sprite.highlighted and cell_sprite != closest_cell_sprite:
                    cell_sprite.remove_highlight()
        else:
            for cell_sprite in cell_sprites_typed:
                if cell_sprite.highlighted:
                    cell_sprite.remove_highlight()

    def prepare_text(
        self,
        font: pygame.font.Font,
        text: str,
        color: pygame.Color,
        height_pct: float,
    ) -> tuple[pygame.Surface, pygame.Rect]:
        """Prepares text for display"""
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        rect.x = self.game.screen.get_width() - 400
        rect.y = self.game.screen.get_height() * height_pct
        return (surface, rect)
