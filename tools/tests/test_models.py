from fightcard.models import Corner
from tests.builders import bout


def test_other_corner() -> None:
    assert Corner.RED.other is Corner.BLUE
    assert Corner.BLUE.other is Corner.RED


def test_swapped_exchanges_fighters_only() -> None:
    original = bout("Ann", "Gym A", "Bea", "Gym B", "C")
    swapped = original.swapped()
    assert (swapped.red, swapped.blue) == (original.blue, original.red)
    assert (swapped.fight_class, swapped.source) == ("C", "test")
