from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ..config import Config
from .scene import Scene

if TYPE_CHECKING:
    from ..game import Game


class MenuScene(Scene):
    """Class that defines the main menu scene"""

    def __init__(self, game: Game) -> None:
        """Instantiates the main menu scene"""
        super().__init__(game)
        self.config = Config.instance().default

        # Fonts
        self.title_font = pygame.font.Font(
            f"assets/fonts/{self.config["title_font"]}",
            self.config["title_font_size"],
        )
        self.default_font = pygame.font.Font(
            f"assets/fonts/{self.config["default_font"]}",
            self.config["default_font_size"],
        )

        # Texts
        self.texts = {}
        self.texts["title"] = self.prepare_text(
            self.title_font,
            self.config["title_text"],
            self.config["default_font_color"],
            0.45,
        )
        self.texts["start"] = self.prepare_text(
            self.default_font,
            self.config["start_text"],
            self.config["default_font_color"],
            0.60,
        )
        self.texts["exit"] = self.prepare_text(
            self.default_font,
            self.config["exit_text"],
            self.config["default_font_color"],
            0.68,
        )

        # Music
        pygame.mixer.music.load(f"assets/sounds/{self.config["background_music"]}")

    # Default methods

    def ready(self) -> None:
        """Set the scene for execution"""
        pygame.mixer.music.play(-1)

    def process_events(self, event: pygame.event.Event) -> None:
        """Processes input events"""
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RETURN:
                pygame.mixer.music.stop()
                self.game.change_scene("MainScene")

            if event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                self.game.is_running = False

    def process_update(self, dt: float) -> None:
        """Processes the sprite update"""
        pass

    def process_draw(self) -> None:
        """Renders the frames of the scene"""
        for text in self.texts.values():
            self.game.screen.blit(text[0], text[1])

    # Local methods

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
        rect.center = (
            self.game.screen.get_width() / 2,
            self.game.screen.get_height() * height_pct,
        )
        return (surface, rect)
