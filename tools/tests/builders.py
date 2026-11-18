"""Shared builders so tests describe bouts in one line."""

from __future__ import annotations

from fightcard.classes import FightClass
from fightcard.models import Bout, Fighter

CLASSES = (
    FightClass("N", "N Class", 15),
    FightClass("C", "C Class", 15),
    FightClass("B", "B Class", 20),
    FightClass("A", "A Class", 30),
)


def bout(red: str, red_gym: str, blue: str, blue_gym: str, fight_class: str = "N") -> Bout:
    """Build a bout from names and gyms."""
    return Bout(Fighter(red, red_gym), Fighter(blue, blue_gym), fight_class, "test")
