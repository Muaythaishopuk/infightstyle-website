"""Order bouts by class and work out when each one starts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING

from fightcard.classes import class_by_code

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fightcard.classes import FightClass
    from fightcard.models import Bout


@dataclass(frozen=True)
class Slot:
    """A bout with its place and times in the running order."""

    number: int
    bout: Bout
    fight_class: FightClass
    start: time
    finish: time


def order_by_class(bouts: Sequence[Bout], classes: Sequence[FightClass]) -> list[Bout]:
    """Sort bouts into the class order given; bouts of one class keep their order."""
    rank = {c.code: index for index, c in enumerate(classes)}
    for bout in bouts:
        class_by_code(tuple(classes), bout.fight_class)
    return sorted(bouts, key=lambda bout: rank[bout.fight_class])


def build_schedule(bouts: Sequence[Bout], classes: Sequence[FightClass], start: time) -> list[Slot]:
    """Give each bout back to back a start and finish time, beginning at ``start``."""
    clock = datetime.combine(date.min, start)
    slots: list[Slot] = []
    for number, bout in enumerate(order_by_class(bouts, classes), start=1):
        fight_class = class_by_code(tuple(classes), bout.fight_class)
        finish = clock + timedelta(minutes=fight_class.minutes)
        slots.append(Slot(number, bout, fight_class, clock.time(), finish.time()))
        clock = finish
    return slots
