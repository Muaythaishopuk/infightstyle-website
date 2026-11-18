from fightcard.config import Billing, Columns, SourceTab
from fightcard.models import TBC
from fightcard.parsing import parse_source

COLUMNS = Columns(fight_class=0, red_name=1, red_gym=2, blue_name=3, blue_gym=4)
HEADER = ["Class", "Name", "Gym", "Name", "Gym"]


def _source(billing: Billing) -> SourceTab:
    return SourceTab(tab="Card ", billing=billing, header_rows=1, columns=COLUMNS)


def test_reads_bouts_and_skips_rows_without_a_class() -> None:
    rows = [
        HEADER,
        ["N Class", " Ann ", "Alpha ", "Bea", "Bravo"],
        [],
        ["", "", "", "", "£4,600"],
        ["C class pro", "Cat", "Charlie", "Dot", "Delta"],
    ]
    result = parse_source(_source(Billing.LISTED), rows)
    assert [(b.red.name, b.red.gym, b.fight_class) for b in result.bouts] == [
        ("Ann", "Alpha", "N"),
        ("Cat", "Charlie", "C"),
    ]
    assert result.bouts[0].source == "Card"
    assert result.warnings == []


def test_headliner_first_tab_is_fought_in_reverse() -> None:
    rows = [HEADER, ["A Class", "Main", "G1", "M2", "G2"], ["A Class", "Co", "G3", "C2", "G4"]]
    result = parse_source(_source(Billing.HEADLINER_FIRST), rows)
    assert [b.red.name for b in result.bouts] == ["Co", "Main"]


def test_missing_name_becomes_tbc_with_a_warning() -> None:
    rows = [HEADER, ["A Class", "Dan", "Alliance", "", "Spain"], ["N Class", "", "", "Eve"]]
    result = parse_source(_source(Billing.LISTED), rows)
    assert result.bouts[0].blue.name == TBC
    assert result.bouts[1].red.name == TBC
    assert result.bouts[1].blue.gym == ""
    assert result.warnings == [
        "Card row 2: fighter from Spain is TBC.",
        "Card row 3: fighter from no gym is TBC.",
    ]
