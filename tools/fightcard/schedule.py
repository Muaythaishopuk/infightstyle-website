"""Order bouts by class, add the intervals and work out when each slot starts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING

from fightcard.classes import class_by_code

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fightcard.classes import FightClass, Interval
    from fightcard.models import Bout


@dataclass(frozen=True)
class Slot:
    """One line of the running order: a bout, or an interval (``bout`` is None)."""

    number: int | None
    bout: Bout | None
    label: str
    start: time
    finish: time


@dataclass(frozen=True)
class _Planned:
    bout: Bout | None
    label: str
    minutes: int


def order_by_class(bouts: Sequence[Bout], classes: Sequence[FightClass]) -> list[Bout]:
    """Sort bouts into the class order given; bouts of one class keep their order."""
    rank = {c.code: index for index, c in enumerate(classes)}
    for bout in bouts:
        class_by_code(tuple(classes), bout.fight_class)
    return sorted(bouts, key=lambda bout: rank[bout.fight_class])


def _plan(
    bouts: Sequence[Bout], classes: Sequence[FightClass], intervals: Sequence[Interval]
) -> list[_Planned]:
    for interval in intervals:
        class_by_code(tuple(classes), interval.after_class)
    ordered = order_by_class(bouts, classes)
    planned: list[_Planned] = []
    for fight_class in classes:
        planned.extend(
            _Planned(bout, fight_class.label, fight_class.minutes)
            for bout in ordered
            if bout.fight_class == fight_class.code
        )
        planned.extend(
            _Planned(None, interval.label, interval.minutes)
            for interval in intervals
            if interval.after_class == fight_class.code
        )
    return planned


def build_schedule(
    bouts: Sequence[Bout],
    classes: Sequence[FightClass],
    start: time,
    intervals: Sequence[Interval] = (),
) -> list[Slot]:
    """Run every slot back to back from ``start``. Only bouts are numbered."""
    clock = datetime.combine(date.min, start)
    slots: list[Slot] = []
    bout_number = 0
    for item in _plan(bouts, classes, intervals):
        finish = clock + timedelta(minutes=item.minutes)
        number = None
        if item.bout is not None:
            bout_number += 1
            number = bout_number
        slots.append(Slot(number, item.bout, item.label, clock.time(), finish.time()))
        clock = finish
    return slots
