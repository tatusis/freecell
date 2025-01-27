from random import shuffle

from .config import Config
from .sprites.card import Card


class Deck:
    """Class that defines a deck of cards"""

    def __init__(self) -> None:
        """Instantiate a deck of cards"""
        self.config = Config.instance().default

        self.suits: list[str] = self.config["suits"]
        self.ranks: list[str] = self.config["ranks"]
        self.cards: list[Card] = []

        for suit in self.suits:
            for rank in self.ranks:
                card = Card(suit, rank)
                self.cards.append(card)

    def shuffle(self) -> None:
        """Shuffle the cards"""
        shuffle(self.cards)
