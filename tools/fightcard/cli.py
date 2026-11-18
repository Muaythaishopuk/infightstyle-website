"""Command line: read the source tabs, write the running-order payload.

Usage::

    python -m fightcard EVENT.json --source "Undercard - =undercard.json" \
        --source "Main card =main.json" --out payload.json [--sheet-id 123]

Each ``--source`` file is the JSON the Google Sheets ``get_values`` tool returns for that
tab. The output holds the cells to write with ``update_formulas``, the formatting requests
for ``update_spreadsheet`` (when ``--sheet-id`` is given) and any warnings. The same input
always gives the same output, so the tab can be rebuilt at any time.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fightcard.config import load_config
from fightcard.corners import assign_corners
from fightcard.formatting import format_requests
from fightcard.parsing import parse_source
from fightcard.schedule import build_schedule
from fightcard.sheet import build_grid

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fightcard.config import EventConfig
    from fightcard.schedule import Slot


class MissingSourceError(ValueError):
    """Raised when a tab named in the event file was not given with --source."""


def _parse_sources(pairs: Sequence[str]) -> dict[str, Path]:
    sources: dict[str, Path] = {}
    for pair in pairs:
        tab, separator, path = pair.rpartition("=")
        if not separator or not tab:
            msg = f"--source must look like 'TAB=path.json', got {pair!r}."
            raise argparse.ArgumentTypeError(msg)
        sources[tab] = Path(path)
    return sources


def _rows(path: Path) -> list[list[str]]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    rows: list[list[str]] = data.get("values", [])
    return rows


def plan(config: EventConfig, sources: dict[str, Path]) -> tuple[list[Slot], list[str]]:
    """Read, correct corners and schedule every bout of the event."""
    bouts = []
    warnings: list[str] = []
    for source in config.sources:
        if source.tab not in sources:
            msg = f"No --source given for tab {source.tab!r}."
            raise MissingSourceError(msg)
        parsed = parse_source(source, _rows(sources[source.tab]))
        bouts.extend(parsed.bouts)
        warnings.extend(parsed.warnings)
    corners = assign_corners(bouts, config.red_corner_gyms, config.red_corner_fighters)
    warnings.extend(corners.warnings)
    return build_schedule(corners.bouts, config.classes, config.start_time), warnings


def preview(slots: Sequence[Slot]) -> list[str]:
    """One readable line per bout, for checking the result by eye."""
    return [
        f"{s.number:>2}  {s.start:%H:%M}-{s.finish:%H:%M}  {s.fight_class.label:<8}  "
        f"RED {s.bout.red.name} ({s.bout.red.gym})  vs  BLUE {s.bout.blue.name} ({s.bout.blue.gym})"
        for s in slots
    ]


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("event", type=Path, help="event settings JSON from events/")
    parser.add_argument("--source", action="append", default=[], help="TAB=get_values.json")
    parser.add_argument("--out", type=Path, required=True, help="where to write the payload")
    parser.add_argument("--sheet-id", type=int, help="numeric id of the output tab")
    args = parser.parse_args(argv)

    config = load_config(args.event)
    slots, warnings = plan(config, _parse_sources(args.source))
    payload: dict[str, Any] = {
        "range": f"'{config.output_tab}'!A1",
        "values": build_grid(slots, config.classes, config.start_time),
        "warnings": warnings,
    }
    if args.sheet_id is not None:
        payload["requests"] = format_requests(args.sheet_id, len(slots), len(config.classes))
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for line in [*preview(slots), *(f"WARNING: {w}" for w in warnings)]:
        print(line)
    return 0
