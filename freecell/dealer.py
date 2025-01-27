from .deck import Deck
from .sprites.card import Card
from .sprites.card_state import CardState
from .sprites.cell import Cell
from .sprites.column_cell import ColumnCell
from .sprites.foundation_cell import FoundationCell
from .sprites.free_cell import FreeCell


class Dealer:
    """Class that manages the main rules of the game"""

    def __init__(self, deck: Deck) -> None:
        """Instantiate the dealer"""
        self.deck = deck

        # Cells
        self.foundation_cells: list[Cell] = []
        self.free_cells: list[Cell] = []
        self.column_cells: list[Cell] = []

        # Card slots in cells
        self.foundation_cell_slots: list[list[Card]] = []
        self.free_cell_slots: list[list[Card]] = []
        self.column_cells_slots: list[list[Card]] = []

        for _ in range(4):
            self.foundation_cell_slots.append([])
            self.free_cell_slots.append([])

        for _ in range(8):
            self.column_cells_slots.append([])

    def prepare_table(self) -> None:
        """Prepare the table for the dealing of cards"""
        # Cell sprites
        for column in range(4):
            foundation_cell = FoundationCell(column)
            self.foundation_cells.append(foundation_cell)

            free_cell = FreeCell(column)
            self.free_cells.append(free_cell)

        for column in range(8):
            Column_cell = ColumnCell(column)
            self.column_cells.append(Column_cell)

    def deal(self) -> None:
        """Deal the cards on the table"""
        idx = 0

        for column in range(8):
            for row in range(7):
                if not (column > 3 and row == 6):
                    card = self.deck.cards[idx]
                    card.idx = idx
                    card._layer = row
                    card.shadow._layer = row - 1
                    card.row = row
                    card.column = column
                    card.cell == self.column_cells[column]
                    card.set_moving_time(-(idx + 10) / 40)
                    card.change_state(CardState.column_cell)
                    card.add_minimal_border()
                    self.column_cells_slots[column].append(card)
                    idx += 1

    # Métodos de verificação

    def is_valid_multiple_card_drag(self, cards_list: list[Card]) -> None:
        """Checks if the cards in the list are in descending order and with alternating suits"""
        is_valid = True

        rank = cards_list[0].rank
        suit_color = cards_list[0].suit_color

        for card in cards_list[1:]:
            if self.deck.ranks.index(card.rank) == self.deck.ranks.index(rank) - 1:
                if card.suit_color != suit_color:
                    rank = card.rank
                    suit_color = card.suit_color
                else:
                    is_valid = False
                    break
            else:
                is_valid = False
                break

        return is_valid

    def can_drag(self, card_sprite: Card) -> tuple[bool, list[Card]]:
        """Checks if a card can be picked up"""
        can_drag = False
        cards_list = None

        match card_sprite.state:
            case CardState.free_cell:
                can_drag = True

            case CardState.column_cell:
                # Trata a carta do topo da célula de coluna
                if card_sprite.row == (len(self.column_cells_slots[card_sprite.column]) - 1):
                    can_drag = True
                else:
                    cards_list = self.column_cells_slots[card_sprite.column][card_sprite.row :]
                    can_drag = self.is_valid_multiple_card_drag(cards_list)

        return (can_drag, cards_list)

    def can_drop_foundation_cell(self, card_being_dragged: Card, cell_sprite: FoundationCell) -> bool:
        """Checks if a card can be dropped into a foundation cell"""
        can_drop = False

        if len(self.foundation_cell_slots[cell_sprite.column]) == 0:
            if card_being_dragged.rank == self.deck.ranks[0]:
                can_drop = True
        else:
            top_card: Card = self.foundation_cell_slots[cell_sprite.column][-1]

            if self.deck.ranks.index(top_card.rank) == self.deck.ranks.index(card_being_dragged.rank) - 1:
                if top_card.suit == card_being_dragged.suit:
                    can_drop = True

        return can_drop

    def can_drop_free_cell(self, cell_sprite: FreeCell) -> bool:
        """Checks if a card can be dropped into a free cell"""
        can_drop = False

        if len(self.free_cell_slots[cell_sprite.column]) == 0:
            can_drop = True

        return can_drop

    def get_valid_cells_count(self, cell_sprite: ColumnCell) -> int:
        """Returns the number of valid cells for movement"""
        valid_cells_count = 0

        for column in range(4):
            if len(self.free_cell_slots[column]) == 0:
                valid_cells_count += 1

        for column in range(8):
            if len(self.column_cells_slots[column]) == 0:
                if column != cell_sprite.column:
                    valid_cells_count += 1

        return valid_cells_count

    def can_drop_column_cell(
        self, card_being_dragged: Card, cell_sprite: ColumnCell, other_cards_being_dragged: list[Card]
    ):
        """Checks if a card can be dropped into a column cell"""
        can_drop = False
        valid_cells_count = self.get_valid_cells_count(cell_sprite)

        if len(other_cards_being_dragged) <= valid_cells_count:
            if len(self.column_cells_slots[cell_sprite.column]) == 0:
                can_drop = True
            else:
                top_card: Card = self.column_cells_slots[cell_sprite.column][-1]

                if self.deck.ranks.index(card_being_dragged.rank) == self.deck.ranks.index(top_card.rank) - 1:
                    if card_being_dragged.suit_color != top_card.suit_color:
                        can_drop = True

        return can_drop

    # Métodos de adição

    def add_card_foundation_cell(self, card_being_dragged: Card, cell_sprite: FoundationCell) -> None:
        """Add a card to a foundation cell"""
        layer = len(self.foundation_cell_slots[cell_sprite.column])
        card_being_dragged._layer = layer
        card_being_dragged.cell = cell_sprite
        self.foundation_cell_slots[cell_sprite.column].append(card_being_dragged)

    def add_card_free_cell(self, card_being_dragged: Card, cell_sprite: FreeCell) -> None:
        """Add a card to a free cell"""
        layer = len(self.free_cell_slots[cell_sprite.column])
        card_being_dragged._layer = layer
        card_being_dragged.cell = cell_sprite
        self.free_cell_slots[cell_sprite.column].append(card_being_dragged)

    def add_card_column_cell(self, card_being_dragged: Card, cell_sprite: Card) -> None:
        """Add a card to a column cell"""
        column_size = len(self.column_cells_slots[cell_sprite.column])
        card_being_dragged.row = column_size
        card_being_dragged._layer = column_size

        card_being_dragged.cell = cell_sprite
        card_being_dragged.column = cell_sprite.column
        self.column_cells_slots[cell_sprite.column].append(card_being_dragged)

    # Métodos de remoção

    def remove_card_foundation_cell(self) -> None:
        """Remove a card from a foundation cell"""
        pass

    def remove_card_free_cell(self, card_being_dragged: Card, cell_sprite: FreeCell) -> None:
        """Remove a card from a free cell"""
        self.free_cell_slots[cell_sprite.column].remove(card_being_dragged)

    def remove_card_column_cell(self, card_being_dragged: Card) -> None:
        """Remove a card from a column cell"""
        self.column_cells_slots[card_being_dragged.column].remove(card_being_dragged)
