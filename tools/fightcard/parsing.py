"""Turn the rows of a source tab into bouts."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from fightcard.classes import parse_class_code
from fightcard.config import Billing
from fightcard.models import TBC, Bout, BoutsResult, Fighter

if TYPE_CHECKING:
    from fightcard.config import SourceTab

Row = Sequence[str]


def _cell(row: Row, index: int) -> str:
    return row[index].strip() if index < len(row) else ""


def _fighter(row: Row, name_col: int, gym_col: int, weight_col: int | None) -> Fighter:
    weight = "" if weight_col is None else _cell(row, weight_col)
    return Fighter(name=_cell(row, name_col) or TBC, gym=_cell(row, gym_col), weight=weight)


def parse_source(source: SourceTab, rows: Sequence[Row]) -> BoutsResult:
    """Read every bout from a tab, in fight order.

    A row counts as a bout when its class column names a class ("N Class", "C class pro").
    Totals and blank rows have none and are skipped. A missing fighter name becomes TBC.
    """
    result = BoutsResult()
    cols = source.columns
    for offset, row in enumerate(rows[source.header_rows :]):
        code = parse_class_code(_cell(row, cols.fight_class))
        if code is None:
            continue
        bout = Bout(
            red=_fighter(row, cols.red_name, cols.red_gym, cols.red_weight),
            blue=_fighter(row, cols.blue_name, cols.blue_gym, cols.blue_weight),
            fight_class=code,
            source=source.tab.strip(),
        )
        sheet_row = source.header_rows + offset + 1
        for fighter in (bout.red, bout.blue):
            if fighter.name == TBC:
                where = f"{source.tab.strip()} row {sheet_row}"
                result.warnings.append(f"{where}: fighter from {fighter.gym or 'no gym'} is TBC.")
        result.bouts.append(bout)
    if source.billing is Billing.HEADLINER_FIRST:
        result.bouts.reverse()
    return result
