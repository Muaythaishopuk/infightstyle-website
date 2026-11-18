"""Building blocks for Google Sheets ``batchUpdate`` requests, shared by every tab."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

Request = dict[str, Any]
Colour = dict[str, float]
Grid = dict[str, int]

DARK: Colour = {"red": 0.15, "green": 0.15, "blue": 0.15}
WHITE: Colour = {"red": 1.0, "green": 1.0, "blue": 1.0}
RED: Colour = {"red": 0.80, "green": 0.0, "blue": 0.0}
BLUE: Colour = {"red": 0.0, "green": 0.27, "blue": 0.80}
LIGHT_RED: Colour = {"red": 0.99, "green": 0.89, "blue": 0.89}
LIGHT_BLUE: Colour = {"red": 0.88, "green": 0.92, "blue": 0.99}
INPUT_YELLOW: Colour = {"red": 1.0, "green": 1.0, "blue": 0.0}  # cells a person may change
RESET_ROWS = 300  # rows cleared of old formatting before styling


def grid_range(sheet_id: int, rows: tuple[int, int], cols: tuple[int, int]) -> Grid:
    """0-based, end-exclusive rows and columns of one tab."""
    return {
        "sheetId": sheet_id,
        "startRowIndex": rows[0],
        "endRowIndex": rows[1],
        "startColumnIndex": cols[0],
        "endColumnIndex": cols[1],
    }


def paint(grid: Grid, fmt: dict[str, Any], fields: str) -> Request:
    """Apply one cell format to a range."""
    return {"repeatCell": {"range": grid, "cell": {"userEnteredFormat": fmt}, "fields": fields}}


def header(grid: Grid, background: Colour) -> Request:
    """Make bold white text on a coloured background."""
    fmt = {
        "backgroundColorStyle": {"rgbColor": background},
        "textFormat": {"bold": True, "foregroundColorStyle": {"rgbColor": WHITE}},
    }
    return paint(grid, fmt, "userEnteredFormat.backgroundColorStyle,userEnteredFormat.textFormat")


def fill(grid: Grid, background: Colour) -> Request:
    """Set the background colour only."""
    fmt = {"backgroundColorStyle": {"rgbColor": background}}
    return paint(grid, fmt, "userEnteredFormat.backgroundColorStyle")


def number_format(grid: Grid, kind: str, pattern: str) -> Request:
    """Set a number format, such as kind TIME with pattern "h:mm am/pm"."""
    fmt = {"numberFormat": {"type": kind, "pattern": pattern}}
    return paint(grid, fmt, "userEnteredFormat.numberFormat")


def reset(sheet_id: int, width: int) -> Request:
    """Clear old formatting so a rebuild leaves no stale colours behind."""
    return paint(grid_range(sheet_id, (0, RESET_ROWS), (0, width)), {}, "userEnteredFormat")


def freeze_header(sheet_id: int) -> Request:
    """Keep the header row in view while scrolling."""
    return {
        "updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount",
        }
    }


def column_widths(sheet_id: int, widths: Sequence[int]) -> list[Request]:
    """Set one width in pixels per column, from column A."""
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
        for index, width in enumerate(widths)
    ]


def frame(sheet_id: int, widths: Sequence[int]) -> list[Request]:
    """Freeze the header row and set every column width: the finish of every tab."""
    return [freeze_header(sheet_id), *column_widths(sheet_id, widths)]
