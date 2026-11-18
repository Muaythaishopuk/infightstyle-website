from fightcard.corners import assign_corners
from fightcard.gyms import gym_key
from fightcard.models import Bout
from tests.builders import bout


def _corner_gyms(bouts: list[Bout]) -> tuple[set[str], set[str]]:
    red = {gym_key(b.red.gym) for b in bouts}
    blue = {gym_key(b.blue.gym) for b in bouts}
    return red, blue


def test_no_gym_ends_up_in_both_corners() -> None:
    bouts = [
        bout("A1", "Alpha", "B1", "Bravo"),
        bout("B2", "Bravo", "C1", "Charlie"),
        bout("C2", "Charlie", "D1", "Delta"),
    ]
    result = assign_corners(bouts)
    red, blue = _corner_gyms(result.bouts)
    assert red.isdisjoint(blue)
    assert result.warnings == []


def test_unpinned_group_keeps_first_listed_red_corner() -> None:
    result = assign_corners([bout("A1", "Alpha", "B1", "Bravo")])
    assert result.bouts[0].red.name == "A1"


def test_pinned_gym_goes_red_whatever_its_spelling() -> None:
    bouts = [bout("X", "Other", "G1", "GFC"), bout("G2", "GFC MUAY THAI", "Y", "Else")]
    result = assign_corners(bouts, red_gyms=["GFC Muay Thai"])
    assert [b.red.name for b in result.bouts] == ["G1", "G2"]


def test_pinned_fighter_puts_their_gym_red() -> None:
    bouts = [bout("Opp", "Lumpinee", "Jake", "Peel"), bout("Zach", "Lumpinee", "Coby", "Mid")]
    result = assign_corners(bouts, red_fighters=["jake"])
    assert result.bouts[0].red.name == "Jake"
    assert result.bouts[1].red.name == "Coby"


def test_unknown_pinned_fighter_is_reported() -> None:
    result = assign_corners([bout("A", "Alpha", "B", "Bravo")], red_fighters=["Nobody"])
    assert result.warnings == ["Nobody is not on the card, so could not be put in the red corner."]


def test_same_gym_bout_is_kept_and_reported() -> None:
    result = assign_corners([bout("A", "DCA", "B", "DCA ")])
    assert result.bouts[0].red.name == "A"
    assert result.warnings == ["Same gym in both corners: A (DCA) vs B (DCA )."]


def test_pinned_gyms_that_meet_each_other_are_reported() -> None:
    result = assign_corners([bout("A", "Alpha", "B", "Bravo")], red_gyms=["Alpha", "Bravo"])
    assert "Gym 'bravo' could not be kept in the red corner." in result.warnings
    assert "Same gym in both corners" not in " ".join(result.warnings)


def test_odd_cycle_is_reported_not_hidden() -> None:
    bouts = [
        bout("A", "Alpha", "B", "Bravo"),
        bout("B2", "Bravo", "C", "Charlie"),
        bout("C2", "Charlie", "A2", "Alpha"),
    ]
    result = assign_corners(bouts)
    assert len(result.warnings) == 1
    assert result.warnings[0].startswith("Same gym in both corners")
