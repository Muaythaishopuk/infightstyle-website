"""Event settings: the measurements that define a floor plan, loaded from a JSON file."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from pathlib import Path

_HEX_COLOUR = re.compile(r"^#[0-9a-fA-F]{6}$")

JsonObject = dict[str, object]


class ConfigError(ValueError):
    """Raised when an event file is missing values or contains impossible ones."""


@dataclass(frozen=True)
class _Measurements:
    """Base for settings sections whose values are all positive numbers."""

    SECTION: ClassVar[str]

    def __post_init__(self) -> None:
        """Reject zero or negative measurements."""
        for name, value in vars(self).items():
            if value <= 0:
                msg = f"{self.SECTION}.{name} must be greater than 0, got {value}"
                raise ConfigError(msg)


@dataclass(frozen=True)
class RoomSpec(_Measurements):
    """The hall. ``width_m`` runs left to right on the plan, ``depth_m`` top to bottom."""

    SECTION = "room"

    width_m: float
    depth_m: float
    perimeter_aisle_m: float


@dataclass(frozen=True)
class RingSpec(_Measurements):
    """The ring, placed in the centre of the room."""

    SECTION = "ring"

    platform_m: float
    ropes_m: float
    clearance_m: float

    def __post_init__(self) -> None:
        """Ropes must fit on the platform."""
        super().__post_init__()
        if self.ropes_m > self.platform_m:
            msg = "ring.ropes_m cannot be larger than ring.platform_m"
            raise ConfigError(msg)


@dataclass(frozen=True)
class WalkwaySpec(_Measurements):
    """The fighters' walkway from the middle of the ring's left side to the tunnel."""

    SECTION = "walkway"

    width_m: float
    barrier_m: float


@dataclass(frozen=True)
class TunnelSpec(_Measurements):
    """The walk-out tunnel against the left-hand wall."""

    SECTION = "tunnel"

    width_m: float
    depth_m: float


@dataclass(frozen=True)
class SeatSpec(_Measurements):
    """Chair size and the aisles that keep rows accessible."""

    SECTION = "seats"

    width_m: float
    row_depth_m: float
    corner_aisle_m: float
    radial_aisle_m: float
    min_block_seats: float

    def __post_init__(self) -> None:
        """Block size must be a whole number of chairs."""
        super().__post_init__()
        if not float(self.min_block_seats).is_integer():
            msg = "seats.min_block_seats must be a whole number"
            raise ConfigError(msg)


@dataclass(frozen=True)
class TierSpec:
    """A ticket tier. ``rows`` of ``None`` means fill all remaining space."""

    name: str
    colour: str
    rows: int | None
    gap_before_m: float

    def __post_init__(self) -> None:
        """Validate the tier."""
        if not self.name.strip():
            msg = "tier name must not be empty"
            raise ConfigError(msg)
        if not _HEX_COLOUR.match(self.colour):
            msg = f"tier {self.name!r} colour must look like #1a2b3c, got {self.colour!r}"
            raise ConfigError(msg)
        if self.rows is not None and self.rows <= 0:
            msg = f"tier {self.name!r} rows must be at least 1, got {self.rows}"
            raise ConfigError(msg)
        if self.gap_before_m < 0:
            msg = f"tier {self.name!r} gap_before_m must not be negative"
            raise ConfigError(msg)


@dataclass(frozen=True)
class EventSpec:
    """Everything needed to draw one event's floor plan."""

    title: str
    date: str
    room: RoomSpec
    ring: RingSpec
    walkway: WalkwaySpec
    tunnel: TunnelSpec
    seats: SeatSpec
    tiers: tuple[TierSpec, ...]

    def __post_init__(self) -> None:
        """Check that the pieces fit together."""
        if not self.tiers:
            msg = "at least one tier is required"
            raise ConfigError(msg)
        names = [tier.name for tier in self.tiers]
        if len(set(names)) != len(names):
            msg = f"tier names must be unique, got {names}"
            raise ConfigError(msg)
        if any(tier.rows is None for tier in self.tiers[:-1]):
            msg = "only the last (outermost) tier may use rows: null to fill the space"
            raise ConfigError(msg)
        if self.ring.platform_m >= min(self.room.width_m, self.room.depth_m):
            msg = "the ring does not fit in the room"
            raise ConfigError(msg)


def _section(raw: JsonObject, key: str) -> JsonObject:
    value = raw.get(key)
    if not isinstance(value, dict):
        msg = f"{key!r} must be an object"
        raise ConfigError(msg)
    return {str(k): v for k, v in value.items()}


def _check_keys(section: str, data: JsonObject, expected: set[str]) -> None:
    missing = expected - data.keys()
    unknown = data.keys() - expected
    if missing or unknown:
        msg = f"{section}: missing {sorted(missing)}, unknown {sorted(unknown)}"
        raise ConfigError(msg)


def _number(section: str, data: JsonObject, key: str) -> float:
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, int | float):
        msg = f"{section}.{key} must be a number, got {value!r}"
        raise ConfigError(msg)
    return float(value)


def _text(section: str, data: JsonObject, key: str) -> str:
    value = data[key]
    if not isinstance(value, str):
        msg = f"{section}.{key} must be text, got {value!r}"
        raise ConfigError(msg)
    return value


def _measurements[T](cls: type[T], raw: JsonObject, key: str) -> T:
    data = _section(raw, key)
    names = [f.name for f in fields(cls)]  # type: ignore[arg-type]
    _check_keys(key, data, set(names))
    return cls(**{name: _number(key, data, name) for name in names})


def _tier(data: object, index: int) -> TierSpec:
    section = f"tiers[{index}]"
    if not isinstance(data, dict):
        msg = f"{section} must be an object"
        raise ConfigError(msg)
    tier = {str(k): v for k, v in data.items()}
    _check_keys(section, tier, {"name", "colour", "rows", "gap_before_m"})
    rows = tier["rows"]
    if rows is not None and (isinstance(rows, bool) or not isinstance(rows, int)):
        msg = f"{section}.rows must be a whole number or null, got {rows!r}"
        raise ConfigError(msg)
    return TierSpec(
        name=_text(section, tier, "name"),
        colour=_text(section, tier, "colour"),
        rows=rows,
        gap_before_m=_number(section, tier, "gap_before_m"),
    )


def parse_event(raw: JsonObject) -> EventSpec:
    """Turn decoded JSON into a validated :class:`EventSpec`."""
    _check_keys(
        "event",
        raw,
        {"title", "date", "room", "ring", "walkway", "tunnel", "seats", "tiers"},
    )
    tiers = raw["tiers"]
    if not isinstance(tiers, list):
        msg = "'tiers' must be a list"
        raise ConfigError(msg)
    return EventSpec(
        title=_text("event", raw, "title"),
        date=_text("event", raw, "date"),
        room=_measurements(RoomSpec, raw, "room"),
        ring=_measurements(RingSpec, raw, "ring"),
        walkway=_measurements(WalkwaySpec, raw, "walkway"),
        tunnel=_measurements(TunnelSpec, raw, "tunnel"),
        seats=_measurements(SeatSpec, raw, "seats"),
        tiers=tuple(_tier(tier, i) for i, tier in enumerate(tiers)),
    )


def load_event(path: Path) -> EventSpec:
    """Read and validate an event JSON file."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        msg = f"{path} is not valid JSON: {error}"
        raise ConfigError(msg) from error
    if not isinstance(raw, dict):
        msg = f"{path} must contain a JSON object"
        raise ConfigError(msg)
    return parse_event({str(k): v for k, v in raw.items()})
