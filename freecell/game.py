import pygame

from .config import Config
from .scenes.main_scene import MainScene
from .scenes.menu_scene import MenuScene
from .scenes.scene import Scene


class Game:
    """Class that controls game execution"""

    def __init__(self) -> None:
        """Instantiate the game"""
        self.config = Config.instance().default

        pygame.mixer.init()
        pygame.init()

        icon = pygame.image.load(f"assets/icons/{self.config["icon"]}")
        pygame.display.set_icon(icon)
        pygame.display.set_caption(self.config["screen_title"])

        self.screen = pygame.display.set_mode(
            size=(self.config["screen_width"], self.config["screen_height"]),
        )
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.fps = self.config["fps"]
        self.scene: Scene = MenuScene(self)

    # Default methods

    def ready(self) -> None:
        """Prepare the game for execution"""
        self.scene.ready()

    def _process_events(self) -> None:
        """Processes input events"""
        for event in pygame.event.get():
            self.scene.process_events(event)

            if event.type == pygame.QUIT:
                self.is_running = False

    def _process_update(self) -> None:
        """Processes the sprite update"""
        dt = self.clock.tick(self.config["fps"]) / 1000
        self.scene.process_update(dt)

    def _process_draw(self) -> None:
        """Renders game frames"""
        self.screen.fill(self.config["screen_color"])
        self.scene.process_draw()
        pygame.display.flip()

    def process(self) -> None:
        """Processes each frame of the game"""
        self._process_events()
        self._process_update()
        self._process_draw()

    def quit(self) -> None:
        """Ends the game execution"""
        pygame.quit()

    # Local methods

    def change_scene(self, scene: str) -> None:
        """Changes the current game scene"""
        if scene == "MainScene":
            self.scene = MainScene(self)
        elif scene == "MenuScene":
            self.scene = MenuScene(self)

        self.scene.ready()
