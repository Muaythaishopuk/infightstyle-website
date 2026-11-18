"""Google Sheets ``batchUpdate`` requests that style the running-order tab."""

from __future__ import annotations

from typing import Any

from fightcard.sheet import CLASS_TABLE_ROW, HEADERS, SETTINGS_COL, START_TIME_ROW

Request = dict[str, Any]

RED = {"red": 0.80, "green": 0.0, "blue": 0.0}
BLUE = {"red": 0.0, "green": 0.27, "blue": 0.80}
LIGHT_RED = {"red": 0.99, "green": 0.89, "blue": 0.89}
LIGHT_BLUE = {"red": 0.88, "green": 0.92, "blue": 0.99}
DARK = {"red": 0.15, "green": 0.15, "blue": 0.15}
WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
INPUT_YELLOW = {"red": 1.0, "green": 1.0, "blue": 0.0}  # cells a person may change
TIME_PATTERN = "h:mm am/pm"
COLUMN_WIDTHS = (50, 80, 80, 80, 170, 190, 170, 190, 30, 140, 130)


def _grid(sheet_id: int, rows: tuple[int, int], cols: tuple[int, int]) -> dict[str, int]:
    return {
        "sheetId": sheet_id,
        "startRowIndex": rows[0],
        "endRowIndex": rows[1],
        "startColumnIndex": cols[0],
        "endColumnIndex": cols[1],
    }


def _paint(grid: dict[str, int], fmt: dict[str, Any], fields: str) -> Request:
    return {"repeatCell": {"range": grid, "cell": {"userEnteredFormat": fmt}, "fields": fields}}


def _header(grid: dict[str, int], background: dict[str, float]) -> Request:
    fmt = {
        "backgroundColorStyle": {"rgbColor": background},
        "textFormat": {"bold": True, "foregroundColorStyle": {"rgbColor": WHITE}},
    }
    fields = "userEnteredFormat.backgroundColorStyle,userEnteredFormat.textFormat"
    return _paint(grid, fmt, fields)


def _fill(grid: dict[str, int], background: dict[str, float]) -> Request:
    fmt = {"backgroundColorStyle": {"rgbColor": background}}
    return _paint(grid, fmt, "userEnteredFormat.backgroundColorStyle")


def _time_format(grid: dict[str, int]) -> Request:
    fmt = {"numberFormat": {"type": "TIME", "pattern": TIME_PATTERN}}
    return _paint(grid, fmt, "userEnteredFormat.numberFormat")


def _widths(sheet_id: int) -> list[Request]:
    return [
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": index,
                    "endIndex": index + 1,
                },
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        }
        for index, width in enumerate(COLUMN_WIDTHS)
    ]


def format_requests(sheet_id: int, bout_count: int, class_count: int) -> list[Request]:
    """Return every request needed to style the tab, in one batch."""
    last_bout_row = bout_count + 1
    settings = (SETTINGS_COL, SETTINGS_COL + 2)
    table_header = CLASS_TABLE_ROW - 2
    return [
        _header(_grid(sheet_id, (0, 1), (0, 4)), DARK),
        _header(_grid(sheet_id, (0, 1), (4, 6)), RED),
        _header(_grid(sheet_id, (0, 1), (6, len(HEADERS))), BLUE),
        _fill(_grid(sheet_id, (1, last_bout_row), (4, 6)), LIGHT_RED),
        _fill(_grid(sheet_id, (1, last_bout_row), (6, len(HEADERS))), LIGHT_BLUE),
        _time_format(_grid(sheet_id, (1, last_bout_row), (1, 3))),
        _header(_grid(sheet_id, (0, 1), settings), DARK),
        _header(_grid(sheet_id, (table_header, table_header + 1), settings), DARK),
        _time_format(_grid(sheet_id, (START_TIME_ROW - 1, START_TIME_ROW), (10, 11))),
        _fill(_grid(sheet_id, (START_TIME_ROW - 1, START_TIME_ROW), (10, 11)), INPUT_YELLOW),
        _fill(
            _grid(sheet_id, (table_header + 1, table_header + 1 + class_count), (10, 11)),
            INPUT_YELLOW,
        ),
        {
            "updateSheetProperties": {
                "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount",
            }
        },
        *_widths(sheet_id),
    ]
