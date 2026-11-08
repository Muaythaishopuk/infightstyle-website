"""Command line: ``python -m venue_layout EVENT.json [--out PLAN.svg]``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from venue_layout.config import ConfigError, load_event
from venue_layout.layout import LayoutError, build_layout
from venue_layout.svg import render_svg


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="venue_layout",
        description="Draw a scaled floor plan for an event from its JSON settings file.",
    )
    parser.add_argument("event", type=Path, help="event settings file (JSON)")
    parser.add_argument(
        "--out",
        type=Path,
        help="where to write the SVG (default: next to the event file, as layout.svg)",
    )
    return parser


def write_if_changed(path: Path, content: str) -> bool:
    """Write ``content`` to ``path`` unless it is already identical. Return True if written."""
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    """Run the command line tool and return the process exit code."""
    args = _parser().parse_args(argv)
    try:
        layout = build_layout(load_event(args.event))
    except (ConfigError, LayoutError) as error:
        sys.stderr.write(f"error: {error}\n")
        return 1
    out: Path = args.out or args.event.with_name("layout.svg")
    changed = write_if_changed(out, render_svg(layout))
    for tier in layout.event.tiers:
        sys.stdout.write(f"{tier.name}: {layout.count(tier.name)} seats\n")
    sys.stdout.write(f"Total: {len(layout.seats)} seats\n")
    sys.stdout.write(f"{'Wrote' if changed else 'Unchanged'}: {out}\n")
    return 0
