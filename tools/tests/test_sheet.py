from datetime import time

from fightcard.schedule import build_schedule
from fightcard.sheet import HEADERS, WIDTH, as_text, build_grid, class_table_range
from tests.builders import CLASSES, bout


def _grid() -> list[list[str | int]]:
    bouts = [bout("Ann", "2 tech", "Bea", "Bravo", "N"), bout("Cat", "C", "Dot", "D", "A")]
    return build_grid(build_schedule(bouts, CLASSES, time(13, 0)), CLASSES, time(13, 0))


def test_text_is_protected_from_number_parsing() -> None:
    assert as_text("1-1") == "'1-1"


def test_lookup_range_covers_every_class() -> None:
    assert class_table_range(CLASSES) == "$J$5:$K$8"


def test_grid_is_rectangular_and_tall_enough_for_settings() -> None:
    grid = _grid()
    assert len(grid) == 8
    assert {len(row) for row in grid} == {WIDTH}
    assert tuple(grid[0][: len(HEADERS)]) == HEADERS


def test_bout_rows_hold_time_formulas() -> None:
    grid = _grid()
    assert grid[1][:8] == [
        1,
        "=$K$2",
        "=B2+TIME(0,VLOOKUP(D2,$J$5:$K$8,2,FALSE),0)",
        "N Class",
        "'Ann",
        "'2 tech",
        "'Bea",
        "'Bravo",
    ]
    assert grid[2][1] == "=C2"


def test_settings_block_holds_the_inputs() -> None:
    grid = _grid()
    assert grid[1][9:] == ["Start time", "13:00"]
    assert grid[3][9:] == ["Class", "Minutes per bout"]
    assert [row[9:] for row in grid[4:8]] == [
        ["N Class", 15],
        ["C Class", 15],
        ["B Class", 20],
        ["A Class", 30],
    ]


def test_long_card_sets_the_grid_height() -> None:
    bouts = [bout(f"F{i}", "x", "y", "z") for i in range(12)]
    grid = build_grid(build_schedule(bouts, CLASSES, time(13, 0)), CLASSES, time(13, 0))
    assert len(grid) == 13
