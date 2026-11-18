"""Shared builders so tests describe bouts in one line."""

from __future__ import annotations

from datetime import time

from fightcard.classes import FightClass, Interval
from fightcard.models import Bout, Fighter
from fightcard.schedule import Slot, build_schedule

CLASSES = (
    FightClass("N", "N Class", 15),
    FightClass("C", "C Class", 15),
    FightClass("B", "B Class", 20),
    FightClass("A", "A Class", 30),
)
INTERVALS = (Interval("N", "Interval 1", 20), Interval("C", "Interval 2", 20))


def bout(red: str, red_gym: str, blue: str, blue_gym: str, fight_class: str = "N") -> Bout:
    """Build a bout from names and gyms."""
    return Bout(Fighter(red, red_gym), Fighter(blue, blue_gym), fight_class, "test")


def schedule(*bouts: Bout) -> list[Slot]:
    """Schedule bouts from 1:30pm with the standard classes and intervals."""
    return build_schedule(bouts, CLASSES, time(13, 30), INTERVALS)
