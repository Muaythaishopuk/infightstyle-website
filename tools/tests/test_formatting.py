import json

from fightcard.formatting import COLUMN_WIDTHS, INTERVAL_GREY, format_requests
from fightcard.schedule import Slot
from fightcard.sheet import WIDTH
from tests.builders import bout, schedule


def _slots() -> list[Slot]:
    return schedule(bout("a", "x", "b", "y", "N"), bout("c", "x", "d", "y", "C"))


def test_every_request_targets_the_given_tab() -> None:
    requests = format_requests(sheet_id=42, slots=_slots(), table_size=6)
    text = json.dumps(requests)
    assert text.count('"sheetId": 42') == len(requests)
    assert '"sheetId": 0' not in text


def test_old_formatting_is_cleared_first() -> None:
    first = format_requests(sheet_id=1, slots=_slots(), table_size=6)[0]["repeatCell"]
    assert first["fields"] == "userEnteredFormat"
    assert first["range"]["startRowIndex"] == 0


def test_corner_columns_cover_every_row() -> None:
    requests = format_requests(sheet_id=1, slots=_slots(), table_size=6)
    red_fill = requests[4]["repeatCell"]["range"]
    assert (red_fill["startRowIndex"], red_fill["endRowIndex"]) == (1, 5)
    assert (red_fill["startColumnIndex"], red_fill["endColumnIndex"]) == (4, 6)


def test_interval_rows_are_grey() -> None:
    requests = format_requests(sheet_id=1, slots=_slots(), table_size=6)
    grey = [
        r["repeatCell"]["range"]["startRowIndex"]
        for r in requests
        if "repeatCell" in r
        and r["repeatCell"]["cell"]["userEnteredFormat"]
        .get("backgroundColorStyle", {})
        .get("rgbColor")
        == INTERVAL_GREY
    ]
    assert grey == [2, 4]


def test_field_masks_have_no_parentheses() -> None:
    requests = format_requests(sheet_id=1, slots=_slots(), table_size=6)
    masks = [r[next(iter(r))]["fields"] for r in requests]
    assert all("(" not in mask for mask in masks)


def test_one_width_per_column() -> None:
    assert len(COLUMN_WIDTHS) == WIDTH
