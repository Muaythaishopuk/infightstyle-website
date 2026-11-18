"""Put each gym in one corner for the whole night.

Every bout links two gyms that must be in opposite corners, so the gyms form a graph that
is two-coloured (red and blue) with a breadth-first search. Gyms the promoter wants in the
red corner are coloured first. In a group of gyms with no such wish, the gym of the first
red-corner fighter listed stays red, so the sheet changes as little as possible.
"""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from fightcard.gyms import gym_key
from fightcard.models import BoutsResult, Corner

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from fightcard.models import Bout


def _describe(bout: Bout) -> str:
    return f"{bout.red.name} ({bout.red.gym}) vs {bout.blue.name} ({bout.blue.gym})"


def _build_graph(bouts: Sequence[Bout]) -> dict[str, list[str]]:
    graph: dict[str, list[str]] = {}
    for bout in bouts:
        red, blue = gym_key(bout.red.gym), gym_key(bout.blue.gym)
        graph.setdefault(red, [])
        graph.setdefault(blue, [])
        if red != blue:
            graph[red].append(blue)
            graph[blue].append(red)
    return graph


def _colour(graph: dict[str, list[str]], seeds: Iterable[str]) -> dict[str, Corner]:
    colours: dict[str, Corner] = {}
    for seed in seeds:
        if seed in colours:
            continue
        colours[seed] = Corner.RED
        queue = deque([seed])
        while queue:
            gym = queue.popleft()
            for neighbour in graph[gym]:
                if neighbour not in colours:
                    colours[neighbour] = colours[gym].other
                    queue.append(neighbour)
    return colours


def _pinned_keys(
    bouts: Sequence[Bout], red_gyms: Iterable[str], red_fighters: Iterable[str]
) -> tuple[list[str], list[str]]:
    keys = [gym_key(gym) for gym in red_gyms]
    warnings: list[str] = []
    fighters = {f.name.casefold(): f for b in bouts for f in (b.red, b.blue)}
    for name in red_fighters:
        fighter = fighters.get(name.casefold())
        if fighter is None:
            warnings.append(f"{name} is not on the card, so could not be put in the red corner.")
        else:
            keys.append(gym_key(fighter.gym))
    return keys, warnings


def assign_corners(
    bouts: Sequence[Bout],
    red_gyms: Iterable[str] = (),
    red_fighters: Iterable[str] = (),
) -> BoutsResult:
    """Swap corners so that no gym appears in both corners, where that is possible.

    ``red_gyms`` and the gyms of ``red_fighters`` are put in the red corner. A bout that
    breaks the rule whatever is done (two fighters from one gym, or wishes that contradict
    each other) keeps its corners and is reported in ``warnings``.
    """
    pinned, warnings = _pinned_keys(bouts, red_gyms, red_fighters)
    graph = _build_graph(bouts)
    pinned_present = [key for key in pinned if key in graph]
    colours = _colour(graph, [*pinned_present, *graph])
    result = BoutsResult(warnings=warnings)
    for key in pinned_present:
        if colours[key] is not Corner.RED:
            result.warnings.append(f"Gym '{key}' could not be kept in the red corner.")
    for bout in bouts:
        red_colour = colours[gym_key(bout.red.gym)]
        blue_colour = colours[gym_key(bout.blue.gym)]
        if red_colour is blue_colour:
            result.bouts.append(bout)
            result.warnings.append(f"Same gym in both corners: {_describe(bout)}.")
        elif red_colour is Corner.RED:
            result.bouts.append(bout)
        else:
            result.bouts.append(bout.swapped())
    return result
