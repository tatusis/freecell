import cv2 as cv
import pygame

from ..config import Config
from ..sprites.cell import Cell


class ColumnCell(pygame.sprite.Sprite, Cell):
    """Class that defines a column cell"""

    def __init__(self, column: int) -> None:
        """Instantiate a column cell"""
        pygame.sprite.Sprite.__init__(self)
        Cell.__init__(self)
        self.config = Config.instance().default
        image_source = cv.imread(f"assets/sprites/{self.config["cell_sprite"]}", cv.IMREAD_UNCHANGED)
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
        self.image.set_alpha(self.config["cell_alpha"])
        self.rect = pygame.Rect(
            0, 0, self.config["card_width"], (self.config["screen_height"] - self.config["card_offset_y"])
        )
        self._layer = -2
        self.column = column
        self.rect.x = column * (self.rect.width + self.config["card_margin_x"]) + self.config["card_offset_x"]
        self.rect.y = self.config["card_offset_y"]

    def add_highlight(self) -> None:
        """Adds highlight to a column cell"""
        self.highlighted = True
        pygame.draw.rect(
            self.image,
            self.config["cell_highlight_color"],
            pygame.Rect(
                self.config["cell_border_width"],
                self.config["cell_border_width"],
                self.config["card_width"] - (2 * self.config["cell_border_width"]),
                self.config["card_height"] - (2 * self.config["cell_border_width"]),
            ),
        )

    def remove_highlight(self) -> None:
        """Remove highlight from a column cell"""
        self.highlighted = False
        self.image = self.default_image.copy()
        self.image.set_alpha(self.config["cell_alpha"])

    def update(self, dt: float) -> None:
        """Processes the sprite update"""
        pass
