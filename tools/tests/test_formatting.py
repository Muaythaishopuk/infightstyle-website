import json

from fightcard.formatting import COLUMN_WIDTHS, format_requests
from fightcard.sheet import WIDTH


def test_every_request_targets_the_given_tab() -> None:
    requests = format_requests(sheet_id=42, bout_count=21, class_count=4)
    text = json.dumps(requests)
    assert text.count('"sheetId": 42') == len(requests)
    assert '"sheetId": 0' not in text


def test_corner_columns_cover_every_bout_row() -> None:
    requests = format_requests(sheet_id=1, bout_count=21, class_count=4)
    red_fill = requests[3]["repeatCell"]["range"]
    assert (red_fill["startRowIndex"], red_fill["endRowIndex"]) == (1, 22)
    assert (red_fill["startColumnIndex"], red_fill["endColumnIndex"]) == (4, 6)


def test_field_masks_have_no_parentheses() -> None:
    requests = format_requests(sheet_id=1, bout_count=3, class_count=4)
    masks = [r[next(iter(r))]["fields"] for r in requests]
    assert all("(" not in mask for mask in masks)


def test_one_width_per_column() -> None:
    assert len(COLUMN_WIDTHS) == WIDTH
