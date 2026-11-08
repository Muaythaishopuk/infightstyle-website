"""Shared test data: a small, valid event that individual tests tweak."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from venue_layout.config import EventSpec, JsonObject, load_event, parse_event

REAL_EVENT = Path(__file__).parents[2] / "planning" / "2026-11-21-fight-league-1" / "event.json"

BASE_EVENT: JsonObject = {
    "title": "Test Night",
    "date": "1 January 2027",
    "room": {"width_m": 30, "depth_m": 28, "perimeter_aisle_m": 1.2},
    "ring": {"platform_m": 7.0, "ropes_m": 6.0, "clearance_m": 2.0},
    "walkway": {"width_m": 2.0, "barrier_m": 0.5},
    "tunnel": {"width_m": 3.0, "depth_m": 2.0},
    "seats": {
        "width_m": 0.5,
        "row_depth_m": 0.9,
        "corner_aisle_m": 1.2,
        "radial_aisle_m": 1.2,
        "min_block_seats": 4,
    },
    "tiers": [
        {"name": "Ringside", "colour": "#d4af37", "rows": 2, "gap_before_m": 0},
        {"name": "Outer ringside", "colour": "#e76f51", "rows": 2, "gap_before_m": 0.6},
        {"name": "Standard", "colour": "#60a5fa", "rows": None, "gap_before_m": 0.6},
    ],
}


def event_data() -> JsonObject:
    """A fresh deep copy of the base event, safe to modify."""
    return copy.deepcopy(BASE_EVENT)


def section(data: JsonObject, key: str) -> dict[str, object]:
    """One settings section of ``data`` (e.g. ``"seats"``), for editing in place."""
    value = data[key]
    assert isinstance(value, dict)
    return value


def tier(data: JsonObject, index: int) -> dict[str, object]:
    """One tier of ``data``, for editing in place."""
    tiers = data["tiers"]
    assert isinstance(tiers, list)
    found = tiers[index]
    assert isinstance(found, dict)
    return found


def event_with(key: str, field: str, value: object) -> EventSpec:
    """The base event with one setting changed; ``key`` is a section name or ``tiers[N]``."""
    data = event_data()
    target = tier(data, int(key[6:-1])) if key.startswith("tiers[") else section(data, key)
    target[field] = value
    return parse_event(data)


@pytest.fixture
def event() -> EventSpec:
    return parse_event(event_data())


@pytest.fixture
def real_event() -> EventSpec:
    return load_event(REAL_EVENT)
