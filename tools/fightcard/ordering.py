"""Rearrange bouts inside their class to meet the promoter's ordering rules.

Two kinds of rule:

- a bout pinned to a place: "Kieran Lydon's bout is fight 4";
- a gap between a gym's bouts: "at least 2 other fights between GFC's bouts", so their
  corner team has time to get the next fighter ready.

Classes keep their places (N bouts stay in the N block). Among the orders that meet every
rule, the one closest to the current order is chosen: each place takes the earliest-listed
bout that still allows the rest to fit. When no order fits, the current order is kept and
a warning says so.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from fightcard.gyms import gym_key

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fightcard.models import Bout


class OrderRules(NamedTuple):
    """Pinned places (fighter name to 1-based bout number) and gaps (gym to bouts between)."""

    pinned: dict[str, int]
    gym_gaps: dict[str, int]


class _Search:
    def __init__(self, bouts: Sequence[Bout], rules: OrderRules) -> None:
        self.bouts = bouts
        self.gaps = {gym_key(gym): gap for gym, gap in rules.gym_gaps.items()}
        names = {name.casefold(): place for name, place in rules.pinned.items()}
        self.place_of: dict[int, int] = {}
        for index, bout in enumerate(bouts):
            for fighter in (bout.red, bout.blue):
                place = names.get(fighter.name.strip().casefold())
                if place is not None:
                    self.place_of[index] = place
        self.reserved = {place: index for index, place in self.place_of.items()}
        self.order: list[int] = []
        self.last_seen: dict[str, int] = {}

    def _gyms(self, index: int) -> set[str]:
        bout = self.bouts[index]
        return {gym_key(bout.red.gym), gym_key(bout.blue.gym)} & self.gaps.keys()

    def _fits(self, index: int, place: int) -> bool:
        bout = self.bouts[index]
        if bout.fight_class != self.bouts[place - 1].fight_class:
            return False
        if self.reserved.get(place, index) != index or self.place_of.get(index, place) != place:
            return False
        return all(
            place - self.last_seen.get(gym, -999) > self.gaps[gym] for gym in self._gyms(index)
        )

    def solve(self, remaining: list[int]) -> bool:
        place = len(self.order) + 1
        if not remaining:
            return True
        for index in remaining:
            if not self._fits(index, place):
                continue
            saved = dict(self.last_seen)
            self.order.append(index)
            self.last_seen.update(dict.fromkeys(self._gyms(index), place))
            if self.solve([i for i in remaining if i != index]):
                return True
            self.order.pop()
            self.last_seen = saved
        return False


def arrange(bouts: Sequence[Bout], rules: OrderRules) -> tuple[list[Bout], list[str]]:
    """Return the bouts in an order that meets ``rules``, plus any warning."""
    search = _Search(bouts, rules)
    found = {f.name.strip().casefold() for b in bouts for f in (b.red, b.blue)}
    warnings = [
        f"{name} is not on the card, so their bout could not be moved to fight {place}."
        for name, place in rules.pinned.items()
        if name.casefold() not in found
    ]
    if search.solve(list(range(len(bouts)))):
        return [bouts[index] for index in search.order], warnings
    warnings.append("The ordering rules cannot all be met; the current order is kept.")
    return list(bouts), warnings
