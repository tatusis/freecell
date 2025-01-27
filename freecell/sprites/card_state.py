from enum import Enum


class CardState(Enum):
    """Class that defines the state of a card"""

    dealer = 0
    drag = 1
    foundation_cell = 2
    free_cell = 3
    column_cell = 4
