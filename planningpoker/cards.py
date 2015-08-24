"""Functions handling game cards (possible estimations)."""
from decimal import Decimal, InvalidOperation


def coerce_card(card: str) -> (str, Decimal):
    """Cast the card string to Decimal if numeric, otherwise leave it as a string."""
    try:
        return Decimal(card)
    except InvalidOperation:
        return card


def coerce_cards(cards: list) -> list:
    """Cast strings in a list to Decimal if they are numeric, otherwise leave them as strings."""
    return [coerce_card(c) for c in cards]
