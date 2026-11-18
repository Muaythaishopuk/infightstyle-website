"""The weigh-in coordinator's tab: every fighter, their weight limit and a box to record it.

Fighters are listed from the last bout of the night to the first, red corner first. The
running order has no weights, so each fighter's weight comes from the bout tabs. A fighter
is matched by name, or through their opponent when their own name changed or is TBC.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from fightcard.cells import Cell, as_text
from fightcard.models import TBC
from fightcard.requests import (
    DARK,
    INPUT_YELLOW,
    LIGHT_BLUE,
    LIGHT_RED,
    Request,
    fill,
    frame,
    grid_range,
    header,
    number_format,
    reset,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from fightcard.models import Bout, Fighter
    from fightcard.schedule import Slot

HEADERS = (
    "Bout",
    "Corner",
    "Fighter",
    "Gym",
    "Weight (kg)",
    "Allowance (kg)",
    "Limit (kg)",
    "Weighed (kg)",
    "Made weight",
)
COLUMN_WIDTHS = (50, 70, 170, 190, 100, 110, 90, 110, 100)
KG_PATTERN = "0.0"
_NUMBER = re.compile(r"\d+(?:\.\d+)?")


@dataclass(frozen=True)
class WeighInRow:
    """One fighter to weigh."""

    bout_number: int
    corner: str
    fighter: Fighter
    weight_kg: float | None
    allowance_kg: float


def parse_weight_kg(text: str) -> float | None:
    """Read "63.5KG ", "67kg" or "59g" (a typo for kg) as kilograms; None if no number."""
    match = _NUMBER.search(text)
    return float(match.group()) if match else None


def _key(name: str) -> str | None:
    cleaned = name.strip().casefold()
    return None if cleaned in {"", TBC.casefold()} else cleaned


def _side_weights(bout: Bout, source: Bout) -> tuple[str, str]:
    """Weights for ``bout``'s red and blue fighters taken from the matching ``source``."""
    source_sides: dict[str | None, Fighter] = {
        _key(source.red.name): source.red,
        _key(source.blue.name): source.blue,
    }
    source_sides.pop(None, None)
    red = source_sides.get(_key(bout.red.name))
    blue = source_sides.get(_key(bout.blue.name))
    if red is None:
        red = source.blue if blue is source.red else source.red
    if blue is None:
        blue = source.red if red is source.blue else source.blue
    return red.weight, blue.weight


def _find_source(bout: Bout, sources: Sequence[Bout]) -> Bout | None:
    names = {_key(bout.red.name), _key(bout.blue.name)} - {None}
    for source in sources:
        if names & {_key(source.red.name), _key(source.blue.name)}:
            return source
    return None


def _describe(bout: Bout) -> str:
    return f"{bout.red.name} vs {bout.blue.name}"


def build_rows(
    slots: Sequence[Slot],
    sources: Sequence[Bout],
    default_allowance_kg: float,
    overrides_kg: Mapping[str, float],
) -> tuple[list[WeighInRow], list[str]]:
    """List every fighter from the last bout to the first, with weight and allowance."""
    overrides = {name.casefold(): kg for name, kg in overrides_kg.items()}
    rows: list[WeighInRow] = []
    warnings: list[str] = []
    for slot in reversed(slots):
        if slot.bout is None or slot.number is None:
            continue
        source = _find_source(slot.bout, sources)
        weights = ("", "") if source is None else _side_weights(slot.bout, source)
        if source is None:
            warnings.append(f"No weight found for bout {slot.number}: {_describe(slot.bout)}.")
        for corner, fighter, weight in zip(
            ("Red", "Blue"), (slot.bout.red, slot.bout.blue), weights, strict=True
        ):
            allowance = overrides.get(fighter.name.casefold(), default_allowance_kg)
            kg = parse_weight_kg(weight)
            if source is not None and kg is None:
                warnings.append(f"No weight for {fighter.name} in bout {slot.number}.")
            rows.append(WeighInRow(slot.number, corner, fighter, kg, allowance))
    return rows, warnings


def build_grid(rows: Sequence[WeighInRow]) -> list[list[Cell]]:
    """Return the whole tab, from A1. Limit and result are formulas."""
    grid: list[list[Cell]] = [list(HEADERS)]
    for sheet_row, row in enumerate(rows, start=2):
        weight: Cell = "" if row.weight_kg is None else row.weight_kg
        limit = f'=IF(E{sheet_row}="","",E{sheet_row}+F{sheet_row})'
        made = (
            f'=IF(OR(H{sheet_row}="",G{sheet_row}=""),"",IF(H{sheet_row}<=G{sheet_row},"Yes","No"))'
        )
        name, gym = as_text(row.fighter.name), as_text(row.fighter.gym)
        grid.append(
            [row.bout_number, row.corner, name, gym, weight, row.allowance_kg, limit, "", made]
        )
    return grid


def format_requests(sheet_id: int, rows: Sequence[WeighInRow]) -> list[Request]:
    """Style the tab: corner colours, kg formats and yellow input cells."""
    data_rows = (1, len(rows) + 1)
    corner_rows = [
        fill(
            grid_range(sheet_id, (index, index + 1), (1, 2)),
            LIGHT_RED if row.corner == "Red" else LIGHT_BLUE,
        )
        for index, row in enumerate(rows, start=1)
    ]
    return [
        reset(sheet_id, len(HEADERS)),
        header(grid_range(sheet_id, (0, 1), (0, len(HEADERS))), DARK),
        *corner_rows,
        number_format(grid_range(sheet_id, data_rows, (4, 8)), "NUMBER", KG_PATTERN),
        fill(grid_range(sheet_id, data_rows, (5, 6)), INPUT_YELLOW),
        fill(grid_range(sheet_id, data_rows, (7, 8)), INPUT_YELLOW),
        *frame(sheet_id, COLUMN_WIDTHS),
    ]
