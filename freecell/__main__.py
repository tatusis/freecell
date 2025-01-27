from .game import Game


def main() -> None:
    """Game entry point"""
    game = Game()
    game.ready()

    while game.is_running:
        game.process()

    game.quit()


if __name__ == "__main__":
    main()
