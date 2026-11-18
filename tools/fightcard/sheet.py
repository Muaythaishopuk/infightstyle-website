"""Lay the running order out as cells for the Google Sheets ``update_formulas`` tool.

Times are formulas, not typed values: change the start time or a class's minutes in the
Settings cells and every start and finish time updates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import time

    from fightcard.classes import FightClass
    from fightcard.schedule import Slot

HEADERS = ("Bout", "Start", "Finish", "Class", "Red corner", "Red gym", "Blue corner", "Blue gym")
SETTINGS_COL = 9  # column J: labels; column K holds the values
START_TIME_ROW = 2
CLASS_TABLE_ROW = 5  # first class row; its header sits on the row above
WIDTH = SETTINGS_COL + 2

Cell = str | int


def as_text(value: str) -> str:
    """Stop Sheets reading names such as "2 tech" or "1-1" as numbers or dates."""
    return f"'{value}"


def class_table_range(classes: Sequence[FightClass]) -> str:
    """A1 range of the class/minutes lookup table in the Settings block."""
    last = CLASS_TABLE_ROW + len(classes) - 1
    return f"$J${CLASS_TABLE_ROW}:$K${last}"


def _slot_row(slot: Slot, sheet_row: int, lookup: str) -> list[Cell]:
    start = "=$K$2" if slot.number == 1 else f"=C{sheet_row - 1}"
    finish = f"=B{sheet_row}+TIME(0,VLOOKUP(D{sheet_row},{lookup},2,FALSE),0)"
    bout = slot.bout
    return [
        slot.number,
        start,
        finish,
        slot.fight_class.label,
        as_text(bout.red.name),
        as_text(bout.red.gym),
        as_text(bout.blue.name),
        as_text(bout.blue.gym),
    ]


def _settings(classes: Sequence[FightClass], start: time) -> dict[int, list[Cell]]:
    rows: dict[int, list[Cell]] = {
        1: ["Settings", ""],
        START_TIME_ROW: ["Start time", start.strftime("%H:%M")],
        CLASS_TABLE_ROW - 1: ["Class", "Minutes per bout"],
    }
    for offset, fight_class in enumerate(classes):
        rows[CLASS_TABLE_ROW + offset] = [fight_class.label, fight_class.minutes]
    return rows


def build_grid(
    slots: Sequence[Slot], classes: Sequence[FightClass], start: time
) -> list[list[Cell]]:
    """Return the whole tab, from A1, as a rectangular grid of cells."""
    lookup = class_table_range(classes)
    settings = _settings(classes, start)
    height = max(len(slots) + 1, *settings)
    grid: list[list[Cell]] = [[""] * WIDTH for _ in range(height)]
    grid[0][: len(HEADERS)] = HEADERS
    for slot in slots:
        sheet_row = slot.number + 1
        grid[sheet_row - 1][: len(HEADERS)] = _slot_row(slot, sheet_row, lookup)
    for sheet_row, cells in settings.items():
        grid[sheet_row - 1][SETTINGS_COL:] = cells
    return grid
