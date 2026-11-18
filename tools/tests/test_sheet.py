from datetime import time

from fightcard.cells import Cell, as_text
from fightcard.schedule import build_schedule
from fightcard.sheet import HEADERS, WIDTH, build_grid, slot_lengths, slot_table_range
from tests.builders import CLASSES, INTERVALS, bout

LENGTHS = slot_lengths(CLASSES, INTERVALS)
LOOKUP = "$J$5:$K$10"


def _grid() -> list[list[Cell]]:
    bouts = [bout("Ann", "2 tech", "Bea", "Bravo", "N"), bout("Cat", "C", "Dot", "D", "A")]
    slots = build_schedule(bouts, CLASSES, time(13, 30), INTERVALS)
    return build_grid(slots, LENGTHS, time(13, 30))


def test_text_is_protected_from_number_parsing() -> None:
    assert as_text("1-1") == "'1-1"


def test_slot_lengths_list_classes_then_intervals() -> None:
    assert [label for label, _ in LENGTHS] == [
        "N Class",
        "C Class",
        "B Class",
        "A Class",
        "Interval 1",
        "Interval 2",
    ]


def test_lookup_range_covers_every_slot() -> None:
    assert slot_table_range(len(LENGTHS)) == LOOKUP


def test_grid_is_rectangular_and_tall_enough_for_settings() -> None:
    grid = _grid()
    assert len(grid) == 10
    assert {len(row) for row in grid} == {WIDTH}
    assert tuple(grid[0][: len(HEADERS)]) == HEADERS


def test_bout_rows_hold_time_formulas() -> None:
    grid = _grid()
    assert grid[1][:8] == [
        1,
        "=$K$2",
        f"=B2+TIME(0,VLOOKUP(D2,{LOOKUP},2,FALSE),0)",
        "N Class",
        "'Ann",
        "'2 tech",
        "'Bea",
        "'Bravo",
    ]


def test_interval_rows_have_times_but_no_number_or_fighters() -> None:
    grid = _grid()
    assert grid[2][:8] == [
        "",
        "=C2",
        f"=B3+TIME(0,VLOOKUP(D3,{LOOKUP},2,FALSE),0)",
        "Interval 1",
        "",
        "",
        "",
        "",
    ]
    assert [row[3] for row in grid[3:5]] == ["Interval 2", "A Class"]
    assert grid[4][0] == 2


def test_settings_block_holds_the_inputs() -> None:
    grid = _grid()
    assert grid[1][9:] == ["Start time", "13:30"]
    assert grid[3][9:] == ["Slot", "Minutes"]
    assert grid[8][9:] == ["Interval 1", 20]


def test_long_card_sets_the_grid_height() -> None:
    bouts = [bout(f"F{i}", "x", "y", "z") for i in range(12)]
    grid = build_grid(build_schedule(bouts, CLASSES, time(13, 0)), LENGTHS, time(13, 0))
    assert len(grid) == 13
