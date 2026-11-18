from fightcard.gyms import gym_key
from fightcard.models import Bout
from fightcard.ordering import OrderRules, arrange
from tests.builders import bout

GFC = "GFC Muay Thai"


def _card() -> list[Bout]:
    gyms = ["DCA", "GFC", "GFC MUAY THAI", "Sitchai", GFC, "Sitchai", "SRMT", "Mac", "Black", GFC]
    return [bout(f"F{i}", gym, f"O{i}", f"Opp{i}") for i, gym in enumerate(gyms, start=1)]


def _gfc_places(bouts: list[Bout]) -> list[int]:
    return [n for n, b in enumerate(bouts, start=1) if gym_key(b.red.gym) == "gfc"]


def test_pinned_bout_and_gym_gap_are_both_met() -> None:
    arranged, warnings = arrange(_card(), OrderRules({"f10": 4}, {GFC: 2}))
    assert warnings == []
    assert arranged[3].red.name == "F10"
    assert _gfc_places(arranged) == [1, 4, 7, 10]
    assert [b.red.name for b in arranged] == [
        "F2",
        "F1",
        "F4",
        "F10",
        "F6",
        "F7",
        "F3",
        "F8",
        "F9",
        "F5",
    ]


def test_an_order_that_already_fits_is_unchanged() -> None:
    card = _card()
    first, _ = arrange(card, OrderRules({"F10": 4}, {GFC: 2}))
    again, _ = arrange(first, OrderRules({"F10": 4}, {GFC: 2}))
    assert again == first
    assert arrange(card, OrderRules({}, {}))[0] == card


def test_bouts_never_leave_their_class() -> None:
    card = [
        bout("n", GFC, "x", "a", "N"),
        bout("c", GFC, "y", "b", "C"),
        bout("c2", "z", "w", "c", "C"),
    ]
    arranged, warnings = arrange(card, OrderRules({}, {GFC: 1}))
    assert [b.red.name for b in arranged] == ["n", "c2", "c"]
    assert warnings == []


def test_impossible_rules_keep_the_order_and_warn() -> None:
    card = [bout("a", GFC, "x", "p"), bout("b", GFC, "y", "q"), bout("c", "r", "z", "s", "C")]
    arranged, warnings = arrange(card, OrderRules({}, {GFC: 1}))
    assert arranged == card
    assert warnings == ["The ordering rules cannot all be met; the current order is kept."]


def test_unknown_pinned_fighter_is_reported() -> None:
    _, warnings = arrange(_card(), OrderRules({"Nobody": 2}, {}))
    assert warnings == ["Nobody is not on the card, so their bout could not be moved to fight 2."]


def test_blue_corner_fighter_can_be_pinned() -> None:
    arranged, _ = arrange(_card(), OrderRules({"O3": 1}, {}))
    assert arranged[0].blue.name == "O3"
