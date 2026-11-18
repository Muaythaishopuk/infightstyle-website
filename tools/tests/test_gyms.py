import pytest

from fightcard.gyms import gym_key


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ("GFC", "GFC MUAY THAI"),
        ("GFC Muay Thai ", "gfc muay thai"),
        ("Nazary Nak Muay Thai", "Nazary Nak muay "),
        ("Alliance MT", "Alliance "),
        ("Johnsons Muay Thai ", "Johnsons"),
        ("Synergy Gym", "synergy"),
        ("DCA ", "D.C.A."),
        ("Johnsons", "Johnson's Muay Thai"),
    ],
)
def test_same_gym_written_differently_shares_a_key(first: str, second: str) -> None:
    assert gym_key(first) == gym_key(second)


def test_different_gyms_keep_different_keys() -> None:
    assert gym_key("Kiet Muay Thai") != gym_key("Kiatphontip")


def test_name_made_only_of_generic_words_is_kept() -> None:
    assert gym_key("Muay Thai Gym") == "muay thai gym"
