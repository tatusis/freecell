import pygame


class Mouse(pygame.sprite.Sprite):
    """Class representing the mouse sprite"""

    def __init__(self) -> None:
        """Instantiate the mouse sprite"""
        super().__init__()
        self.rect = pygame.Rect(0, 0, 1, 1)
