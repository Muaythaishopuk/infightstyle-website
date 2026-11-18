"""Load an event's settings from its JSON file in ``events/``."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import time
from enum import Enum
from typing import TYPE_CHECKING, Any

from fightcard.classes import FightClass

if TYPE_CHECKING:
    from pathlib import Path


class Billing(Enum):
    """How a source tab lists its bouts."""

    LISTED = "listed"
    """Bouts are listed in the order they will be fought."""
    HEADLINER_FIRST = "headliner_first"
    """The top bout is the main event, so it is fought last."""


@dataclass(frozen=True)
class Columns:
    """0-based column positions of each field in a source tab."""

    fight_class: int
    red_name: int
    red_gym: int
    blue_name: int
    blue_gym: int


@dataclass(frozen=True)
class SourceTab:
    """A tab of the spreadsheet that lists bouts."""

    tab: str
    billing: Billing
    header_rows: int
    columns: Columns


@dataclass(frozen=True)
class EventConfig:
    """Everything needed to build one event's running order."""

    name: str
    output_tab: str
    start_time: time
    classes: tuple[FightClass, ...]
    sources: tuple[SourceTab, ...]
    red_corner_gyms: tuple[str, ...]
    red_corner_fighters: tuple[str, ...]


def _source(raw: dict[str, Any]) -> SourceTab:
    return SourceTab(
        tab=raw["tab"],
        billing=Billing(raw["billing"]),
        header_rows=int(raw["header_rows"]),
        columns=Columns(**raw["columns"]),
    )


def parse_config(raw: dict[str, Any]) -> EventConfig:
    """Build an EventConfig from already-decoded JSON."""
    return EventConfig(
        name=raw["name"],
        output_tab=raw["output_tab"],
        start_time=time.fromisoformat(raw["start_time"]),
        classes=tuple(FightClass(**c) for c in raw["classes"]),
        sources=tuple(_source(s) for s in raw["sources"]),
        red_corner_gyms=tuple(raw.get("red_corner_gyms", ())),
        red_corner_fighters=tuple(raw.get("red_corner_fighters", ())),
    )


def load_config(path: Path) -> EventConfig:
    """Read and parse an event JSON file."""
    return parse_config(json.loads(path.read_text(encoding="utf-8")))
