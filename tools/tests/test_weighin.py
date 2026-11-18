import pytest

from fightcard.models import TBC, Bout, Fighter
from fightcard.weighin import HEADERS, build_grid, build_rows, format_requests, parse_weight_kg
from tests.builders import bout, schedule


def _weighed(red: str, red_kg: str, blue: str, blue_kg: str) -> Bout:
    return Bout(Fighter(red, "x", red_kg), Fighter(blue, "y", blue_kg), "N", "source")


@pytest.mark.parametrize(
    ("text", "kg"),
    [("67kg", 67.0), ("63.5KG ", 63.5), ("59g", 59.0), (" 70 kg", 70.0), ("", None), ("tbc", None)],
)
def test_reads_weights(text: str, kg: float | None) -> None:
    assert parse_weight_kg(text) == kg


def test_last_bout_first_red_before_blue_and_intervals_skipped() -> None:
    slots = schedule(bout("Ann", "a", "Bea", "b", "N"), bout("Cat", "c", "Dot", "d", "C"))
    sources = [_weighed("Ann", "60kg", "Bea", "60kg"), _weighed("Cat", "70kg", "Dot", "70kg")]
    rows, warnings = build_rows(slots, sources, 0.5, {})
    assert [(r.bout_number, r.corner, r.fighter.name) for r in rows] == [
        (2, "Red", "Cat"),
        (2, "Blue", "Dot"),
        (1, "Red", "Ann"),
        (1, "Blue", "Bea"),
    ]
    assert warnings == []


def test_weights_follow_fighters_when_corners_were_swapped() -> None:
    rows, _ = build_rows(
        schedule(bout("Bea", "b", "Ann", "a")), [_weighed("Ann", "60", "Bea", "61")], 0.5, {}
    )
    assert [(r.fighter.name, r.weight_kg) for r in rows] == [("Bea", 61.0), ("Ann", 60.0)]


@pytest.mark.parametrize("other", ["Baily Fletcher", TBC])
@pytest.mark.parametrize("other_is_red", [True, False])
@pytest.mark.parametrize("source_swapped", [True, False])
def test_renamed_or_tbc_fighter_takes_the_other_side_of_the_matched_bout(
    other: str, *, other_is_red: bool, source_swapped: bool
) -> None:
    source = _weighed("Baily", "65kg", "Lewis", "66kg")
    source = source.swapped() if source_swapped else source
    pair = bout(other, "x", "Lewis", "y")
    pair = pair if other_is_red else pair.swapped()
    rows, _ = build_rows(schedule(pair), [source], 0.5, {})
    assert {r.fighter.name: r.weight_kg for r in rows} == {other: 65.0, "Lewis": 66.0}


def test_tbc_in_two_bouts_do_not_match_each_other() -> None:
    slots = schedule(bout(TBC, "x", "Ollie", "y"))
    sources = [_weighed(TBC, "57kg", "Dan", "57kg"), _weighed(TBC, "67kg", "Ollie", "67kg")]
    rows, _ = build_rows(slots, sources, 0.5, {})
    assert [r.weight_kg for r in rows] == [67.0, 67.0]


def test_allowance_overrides_by_name() -> None:
    rows, _ = build_rows(
        schedule(bout("Jake", "x", "Louie", "y")),
        [_weighed("Jake", "67", "Louie", "67")],
        0.5,
        {"jake": 0},
    )
    assert [r.allowance_kg for r in rows] == [0.0, 0.5]


def test_missing_bout_and_missing_weight_are_reported() -> None:
    slots = schedule(bout("Ann", "x", "Bea", "y"), bout("Cat", "x", "Dot", "y"))
    rows, warnings = build_rows(slots, [_weighed("Cat", "", "Dot", "70kg")], 0.5, {})
    assert [r.weight_kg for r in rows] == [None, 70.0, None, None]
    assert warnings == ["No weight for Cat in bout 2.", "No weight found for bout 1: Ann vs Bea."]


def test_grid_has_formulas_for_limit_and_result() -> None:
    rows, _ = build_rows(
        schedule(bout("Ann", "1-1", "Bea", "y")), [_weighed("Ann", "60", "Bea", "")], 0.5, {}
    )
    grid = build_grid(rows)
    assert tuple(grid[0]) == HEADERS
    assert grid[1] == [
        1,
        "Red",
        "'Ann",
        "'1-1",
        60.0,
        0.5,
        '=IF(E2="","",E2+F2)',
        "",
        '=IF(OR(H2="",G2=""),"",IF(H2<=G2,"Yes","No"))',
    ]
    assert grid[2][4] == ""


def test_corner_cells_are_coloured_per_row() -> None:
    rows, _ = build_rows(
        schedule(bout("Ann", "x", "Bea", "y")), [_weighed("Ann", "60", "Bea", "60")], 0.5, {}
    )
    requests = format_requests(5, rows)
    fills = [r["repeatCell"] for r in requests[2:4]]
    assert [f["range"]["startRowIndex"] for f in fills] == [1, 2]
    assert fills[0]["cell"] != fills[1]["cell"]
    assert all(
        r[next(iter(r))].get("range", {"sheetId": 5}).get("sheetId", 5) == 5 for r in requests
    )
