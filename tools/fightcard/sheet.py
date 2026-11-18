"""Lay the running order out as cells for the Google Sheets ``update_formulas`` tool.

Times are formulas, not typed values: change the start time or a slot's minutes in the
Settings cells and every start and finish time updates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fightcard.cells import Cell, as_text

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import time

    from fightcard.classes import FightClass, Interval
    from fightcard.schedule import Slot

HEADERS = ("Bout", "Start", "Finish", "Class", "Red corner", "Red gym", "Blue corner", "Blue gym")
SETTINGS_COL = 9  # column J: labels; column K holds the values
START_TIME_ROW = 2
FIRST_DATA_ROW = 2
SLOT_TABLE_ROW = 5  # first row of the slot-length table; its header sits on the row above
WIDTH = SETTINGS_COL + 2


def slot_lengths(
    classes: Sequence[FightClass], intervals: Sequence[Interval]
) -> list[tuple[str, int]]:
    """Every slot label with its minutes, as listed in the Settings block."""
    return [(c.label, c.minutes) for c in classes] + [(i.label, i.minutes) for i in intervals]


def slot_table_range(size: int) -> str:
    """A1 range of the label/minutes lookup table in the Settings block."""
    return f"$J${SLOT_TABLE_ROW}:$K${SLOT_TABLE_ROW + size - 1}"


def _slot_row(slot: Slot, sheet_row: int, lookup: str) -> list[Cell]:
    start = "=$K$2" if sheet_row == FIRST_DATA_ROW else f"=C{sheet_row - 1}"
    finish = f"=B{sheet_row}+TIME(0,VLOOKUP(D{sheet_row},{lookup},2,FALSE),0)"
    times: list[Cell] = [start, finish, slot.label]
    if slot.bout is None:
        return ["", *times, "", "", "", ""]
    red, blue = slot.bout.red, slot.bout.blue
    fighters = [as_text(red.name), as_text(red.gym), as_text(blue.name), as_text(blue.gym)]
    return [slot.number or "", *times, *fighters]


def _settings(lengths: Sequence[tuple[str, int]], start: time) -> dict[int, list[Cell]]:
    rows: dict[int, list[Cell]] = {
        1: ["Settings", ""],
        START_TIME_ROW: ["Start time", start.strftime("%H:%M")],
        SLOT_TABLE_ROW - 1: ["Slot", "Minutes"],
    }
    for offset, (label, minutes) in enumerate(lengths):
        rows[SLOT_TABLE_ROW + offset] = [label, minutes]
    return rows


def build_grid(
    slots: Sequence[Slot], lengths: Sequence[tuple[str, int]], start: time
) -> list[list[Cell]]:
    """Return the whole tab, from A1, as a rectangular grid of cells."""
    lookup = slot_table_range(len(lengths))
    settings = _settings(lengths, start)
    height = max(len(slots) + 1, *settings)
    grid: list[list[Cell]] = [[""] * WIDTH for _ in range(height)]
    grid[0][: len(HEADERS)] = HEADERS
    for index, slot in enumerate(slots):
        sheet_row = index + FIRST_DATA_ROW
        grid[sheet_row - 1][: len(HEADERS)] = _slot_row(slot, sheet_row, lookup)
    for sheet_row, cells in settings.items():
        grid[sheet_row - 1][SETTINGS_COL:] = cells
    return grid
