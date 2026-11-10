import json
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.conftest import REAL_EVENT, event_data, section, tier
from venue_layout.config import ConfigError, JsonObject, load_event, parse_event

Mutation = Callable[[JsonObject], None]


def _set(key: str, field: str, value: object) -> Mutation:
    return lambda data: section(data, key).__setitem__(field, value)


def _set_tier(index: int, field: str, value: object) -> Mutation:
    return lambda data: tier(data, index).__setitem__(field, value)


def test_real_event_file_is_valid() -> None:
    event = load_event(REAL_EVENT)
    assert event.room.width_m == 30
    assert event.room.depth_m == 28
    assert [tier.name for tier in event.tiers] == ["Ringside", "Outer ringside", "Standard"]


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (_set("room", "width_m", 0), "room.width_m must be greater than 0"),
        (_set("room", "width_m", "30"), "must be a number"),
        (_set("room", "width_m", True), "must be a number"),  # noqa: FBT003
        (_set("room", "extra", 1), "unknown \\['extra'\\]"),
        (lambda d: section(d, "room").pop("depth_m"), "missing \\['depth_m'\\]"),
        (lambda d: d.__setitem__("room", []), "'room' must be an object"),
        (lambda d: d.__setitem__("title", 5), "event.title must be text"),
        (lambda d: d.__setitem__("tiers", {}), "'tiers' must be a list"),
        (lambda d: d.__setitem__("tiers", []), "at least one tier"),
        (lambda d: d.__setitem__("tiers", [1]), "tiers\\[0\\] must be an object"),
        (_set("ring", "ropes_m", 8), "ropes_m cannot be larger"),
        (_set("ring", "platform_m", 28), "ring does not fit"),
        (_set("seats", "min_block_seats", 2.5), "whole number"),
        (_set_tier(0, "colour", "gold"), "colour must look like"),
        (_set_tier(0, "name", " "), "name must not be empty"),
        (_set_tier(0, "rows", 0), "rows must be at least 1"),
        (_set_tier(0, "target_seats", 1.5), "whole number or null"),
        (_set_tier(0, "rows", 1.5), "whole number or null"),
        (_set_tier(0, "target_seats", 0), "target_seats must be > 0"),
        (_set_tier(0, "sides", []), "at least one side"),
        (_set_tier(0, "sides", ["top", "top"]), "lists a side twice"),
        (_set_tier(0, "sides", ["north"]), "sides must be a list"),
        (_set_tier(0, "sides", "top"), "sides must be a list"),
        (_set("bleachers", "depth_m", 12), "bleachers reach the ring"),
        (_set_tier(0, "gap_before_m", -1), "must not be negative"),
        (_set_tier(1, "name", "Ringside"), "must be unique"),
    ],
)
def test_bad_settings_are_rejected(mutate: Mutation, message: str) -> None:
    data = event_data()
    mutate(data)
    with pytest.raises(ConfigError, match=message):
        parse_event(data)


def test_load_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "event.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigError, match="not valid JSON"):
        load_event(path)


def test_load_rejects_non_object(tmp_path: Path) -> None:
    path = tmp_path / "event.json"
    path.write_text(json.dumps([1, 2]), encoding="utf-8")
    with pytest.raises(ConfigError, match="must contain a JSON object"):
        load_event(path)
