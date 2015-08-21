"""Test the ``planningpoker.views.moderator.coerce_cards`` function."""
from decimal import Decimal

import pytest

from planningpoker.views.moderator import coerce_cards


@pytest.mark.parametrize('cards, coerced_cards', [
    ([1, 2, 3], [Decimal(1), Decimal(2), Decimal(3)]),
    (['1', '2', '3'], [Decimal(1), Decimal(2), Decimal(3)]),
    ([1, '2', 'dunno'], [Decimal(1), Decimal(2), 'dunno']),
])
def test_coerce_cards(cards, coerced_cards):
    """Check if coercing the cards casts numbers to Decimals and leaves the strings intact."""
    assert coerce_cards(cards) == coerced_cards
