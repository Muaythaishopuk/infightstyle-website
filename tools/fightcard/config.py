"""Load an event's settings from its JSON file in ``events/``."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import TYPE_CHECKING, Any

from fightcard.classes import FightClass, Interval

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
    red_weight: int | None = None
    blue_weight: int | None = None


@dataclass(frozen=True)
class SourceTab:
    """A tab of the spreadsheet that lists bouts."""

    tab: str
    billing: Billing
    header_rows: int
    columns: Columns


@dataclass(frozen=True)
class WeighInConfig:
    """Settings for the weigh-in coordinator's tab."""

    output_tab: str
    default_allowance_kg: float
    allowance_overrides_kg: dict[str, float]
    weight_sources: tuple[SourceTab, ...]


@dataclass(frozen=True)
class PosterConfig:
    """Wording and font for the public running-order post."""

    title: str
    subtitle: str
    font: str


@dataclass(frozen=True)
class EventConfig:
    """Everything needed to build one event's running order."""

    name: str
    output_tab: str
    start_time: time
    classes: tuple[FightClass, ...]
    intervals: tuple[Interval, ...]
    sources: tuple[SourceTab, ...]
    red_corner_gyms: tuple[str, ...]
    red_corner_fighters: tuple[str, ...]
    pinned_bouts: dict[str, int] = field(default_factory=dict)
    gym_gaps: dict[str, int] = field(default_factory=dict)
    default_gym_gap: int = 0
    weigh_in: WeighInConfig | None = None
    poster: PosterConfig | None = None


def _source(raw: dict[str, Any]) -> SourceTab:
    return SourceTab(
        tab=raw["tab"],
        billing=Billing(raw["billing"]),
        header_rows=int(raw["header_rows"]),
        columns=Columns(**raw["columns"]),
    )


def _weigh_in(raw: dict[str, Any] | None) -> WeighInConfig | None:
    if raw is None:
        return None
    return WeighInConfig(
        output_tab=raw["output_tab"],
        default_allowance_kg=float(raw["default_allowance_kg"]),
        allowance_overrides_kg={k: float(v) for k, v in raw["allowance_overrides_kg"].items()},
        weight_sources=tuple(_source(s) for s in raw["weight_sources"]),
    )


def parse_config(raw: dict[str, Any]) -> EventConfig:
    """Build an EventConfig from already-decoded JSON."""
    return EventConfig(
        name=raw["name"],
        output_tab=raw["output_tab"],
        start_time=time.fromisoformat(raw["start_time"]),
        classes=tuple(FightClass(**c) for c in raw["classes"]),
        intervals=tuple(Interval(**i) for i in raw.get("intervals", ())),
        sources=tuple(_source(s) for s in raw["sources"]),
        red_corner_gyms=tuple(raw.get("red_corner_gyms", ())),
        red_corner_fighters=tuple(raw.get("red_corner_fighters", ())),
        pinned_bouts={k: int(v) for k, v in raw.get("pinned_bouts", {}).items()},
        gym_gaps={k: int(v) for k, v in raw.get("gym_gaps", {}).items()},
        default_gym_gap=int(raw.get("default_gym_gap", 0)),
        weigh_in=_weigh_in(raw.get("weigh_in")),
        poster=PosterConfig(**raw["poster"]) if "poster" in raw else None,
    )


def load_config(path: Path) -> EventConfig:
    """Read and parse an event JSON file."""
    return parse_config(json.loads(path.read_text(encoding="utf-8")))
