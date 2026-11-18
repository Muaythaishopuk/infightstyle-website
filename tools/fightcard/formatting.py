"""Google Sheets ``batchUpdate`` requests that style the running-order tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fightcard import requests as rq
from fightcard.sheet import (
    FIRST_DATA_ROW,
    HEADERS,
    SETTINGS_COL,
    SLOT_TABLE_ROW,
    START_TIME_ROW,
    WIDTH,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fightcard.schedule import Slot

INTERVAL_GREY = {"red": 0.85, "green": 0.85, "blue": 0.85}
TIME_PATTERN = "h:mm am/pm"
COLUMN_WIDTHS = (50, 80, 80, 80, 170, 190, 170, 190, 30, 140, 130)
VALUE_COL = (SETTINGS_COL + 1, SETTINGS_COL + 2)


def _interval(grid: rq.Grid) -> rq.Request:
    fmt = {"backgroundColorStyle": {"rgbColor": INTERVAL_GREY}, "textFormat": {"bold": True}}
    return rq.paint(
        grid, fmt, "userEnteredFormat.backgroundColorStyle,userEnteredFormat.textFormat"
    )


def format_requests(sheet_id: int, slots: Sequence[Slot], table_size: int) -> list[rq.Request]:
    """Return every request needed to style the tab, in one batch."""
    data_rows = (FIRST_DATA_ROW - 1, len(slots) + 1)
    settings = (SETTINGS_COL, SETTINGS_COL + 2)
    start_row = (START_TIME_ROW - 1, START_TIME_ROW)
    table_header = SLOT_TABLE_ROW - 2
    table_rows = (table_header + 1, table_header + 1 + table_size)
    intervals = [
        _interval(rq.grid_range(sheet_id, (row, row + 1), (0, len(HEADERS))))
        for row, slot in enumerate(slots, start=FIRST_DATA_ROW - 1)
        if slot.bout is None
    ]
    return [
        rq.reset(sheet_id, WIDTH),
        rq.header(rq.grid_range(sheet_id, (0, 1), (0, 4)), rq.DARK),
        rq.header(rq.grid_range(sheet_id, (0, 1), (4, 6)), rq.RED),
        rq.header(rq.grid_range(sheet_id, (0, 1), (6, len(HEADERS))), rq.BLUE),
        rq.fill(rq.grid_range(sheet_id, data_rows, (4, 6)), rq.LIGHT_RED),
        rq.fill(rq.grid_range(sheet_id, data_rows, (6, len(HEADERS))), rq.LIGHT_BLUE),
        *intervals,
        rq.number_format(rq.grid_range(sheet_id, data_rows, (1, 3)), "TIME", TIME_PATTERN),
        rq.header(rq.grid_range(sheet_id, (0, 1), settings), rq.DARK),
        rq.header(rq.grid_range(sheet_id, (table_header, table_header + 1), settings), rq.DARK),
        rq.number_format(rq.grid_range(sheet_id, start_row, VALUE_COL), "TIME", TIME_PATTERN),
        rq.fill(rq.grid_range(sheet_id, start_row, VALUE_COL), rq.INPUT_YELLOW),
        rq.fill(rq.grid_range(sheet_id, table_rows, VALUE_COL), rq.INPUT_YELLOW),
        *rq.frame(sheet_id, COLUMN_WIDTHS),
    ]
