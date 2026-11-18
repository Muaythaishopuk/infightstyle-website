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
from fightcard.ordering import OrderRules, arrange
from fightcard.parsing import parse_source
from fightcard.poster import PosterStyle, poster_lines, render
from fightcard.schedule import build_schedule, order_by_class
from fightcard.sheet import build_grid, slot_lengths
from fightcard.weighin import build_grid as build_weigh_in_grid
from fightcard.weighin import build_rows
from fightcard.weighin import format_requests as weigh_in_requests

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fightcard.config import EventConfig, PosterConfig, SourceTab, WeighInConfig
    from fightcard.models import Bout
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


def _read(
    tabs: Sequence[SourceTab], sources: dict[str, Path], warnings: list[str] | None
) -> list[Bout]:
    bouts: list[Bout] = []
    for source in tabs:
        if source.tab not in sources:
            msg = f"No --source given for tab {source.tab!r}."
            raise MissingSourceError(msg)
        parsed = parse_source(source, _rows(sources[source.tab]))
        bouts.extend(parsed.bouts)
        if warnings is not None:
            warnings.extend(parsed.warnings)
    return bouts


def plan(config: EventConfig, sources: dict[str, Path]) -> tuple[list[Slot], list[str]]:
    """Read, correct corners and schedule every bout of the event."""
    warnings: list[str] = []
    bouts = _read(config.sources, sources, warnings)
    corners = assign_corners(bouts, config.red_corner_gyms, config.red_corner_fighters)
    warnings.extend(corners.warnings)
    rules = OrderRules(pinned=config.pinned_bouts, gym_gaps=config.gym_gaps)
    arranged, order_warnings = arrange(order_by_class(corners.bouts, config.classes), rules)
    warnings.extend(order_warnings)
    slots = build_schedule(arranged, config.classes, config.start_time, config.intervals)
    return slots, warnings


def preview(slots: Sequence[Slot]) -> list[str]:
    """One readable line per bout, for checking the result by eye."""
    return [_preview_line(slot) for slot in slots]


def _preview_line(slot: Slot) -> str:
    times = f"{slot.start:%H:%M}-{slot.finish:%H:%M}  {slot.label:<10}"
    if slot.bout is None:
        return f"    {times}"
    red, blue = slot.bout.red, slot.bout.blue
    return (
        f"{slot.number:>2}  {times}  RED {red.name} ({red.gym})  vs  BLUE {blue.name} ({blue.gym})"
    )


def _weigh_in(
    weigh_in: WeighInConfig,
    sources: dict[str, Path],
    slots: Sequence[Slot],
    sheet_id: int | None,
    warnings: list[str],
) -> dict[str, Any]:
    weight_bouts = _read(weigh_in.weight_sources, sources, None)
    rows, row_warnings = build_rows(
        slots, weight_bouts, weigh_in.default_allowance_kg, weigh_in.allowance_overrides_kg
    )
    warnings.extend(row_warnings)
    result: dict[str, Any] = {
        "range": f"'{weigh_in.output_tab}'!A1",
        "values": build_weigh_in_grid(rows),
    }
    if sheet_id is not None:
        result["requests"] = weigh_in_requests(sheet_id, rows)
    return result


class PosterSettingsError(ValueError):
    """Raised when a post is asked for without the settings it needs."""


def _poster(
    settings: PosterConfig | None, slots: Sequence[Slot], background: Path | None, out: Path
) -> None:
    if settings is None or background is None:
        msg = "--poster-out needs --poster-background and a 'poster' block in the event file."
        raise PosterSettingsError(msg)
    style = PosterStyle(font=Path(settings.font), title=settings.title, subtitle=settings.subtitle)
    render(poster_lines(slots, style.labels), background, out, style)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("event", type=Path, help="event settings JSON from events/")
    parser.add_argument("--source", action="append", default=[], help="TAB=get_values.json")
    parser.add_argument("--out", type=Path, required=True, help="where to write the payload")
    parser.add_argument("--sheet-id", type=int, help="numeric id of the running-order tab")
    parser.add_argument("--weigh-in-sheet-id", type=int, help="numeric id of the weigh-in tab")
    parser.add_argument("--poster-background", type=Path, help="background image for the post")
    parser.add_argument("--poster-out", type=Path, help="where to save the post image")
    args = parser.parse_args(argv)

    config = load_config(args.event)
    sources = _parse_sources(args.source)
    slots, warnings = plan(config, sources)
    lengths = slot_lengths(config.classes, config.intervals)
    payload: dict[str, Any] = {
        "range": f"'{config.output_tab}'!A1",
        "values": build_grid(slots, lengths, config.start_time),
        "warnings": warnings,
    }
    if args.sheet_id is not None:
        payload["requests"] = format_requests(args.sheet_id, slots, len(lengths))
    if config.weigh_in is not None:
        payload["weigh_in"] = _weigh_in(
            config.weigh_in, sources, slots, args.weigh_in_sheet_id, warnings
        )
    if args.poster_out is not None:
        _poster(config.poster, slots, args.poster_background, args.poster_out)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for line in [*preview(slots), *(f"WARNING: {w}" for w in warnings)]:
        print(line)
    return 0
