"""Work out where the ring, walkway, tunnel and every chair go."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from venue_layout.geometry import Rect

if TYPE_CHECKING:
    from collections.abc import Iterator

    from venue_layout.config import EventSpec, SeatSpec, TierSpec


class LayoutError(ValueError):
    """Raised when the requested tiers cannot physically fit in the room."""


class Side(StrEnum):
    """Which side of the ring a seat faces from."""

    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True)
class Seat:
    """One chair. ``row`` counts from 1 at the front of its tier."""

    tier: str
    row: int
    side: Side
    rect: Rect


@dataclass(frozen=True)
class Layout:
    """A fully placed floor plan."""

    event: EventSpec
    room: Rect
    seating_area: Rect
    ring: Rect
    ropes: Rect
    walkway: Rect
    tunnel: Rect
    seats: tuple[Seat, ...]

    def count(self, tier: str) -> int:
        """Number of chairs in ``tier``."""
        return sum(1 for seat in self.seats if seat.tier == tier)

    def rows(self, tier: str) -> int:
        """Deepest row number used by ``tier`` (0 if it has no seats)."""
        return max((seat.row for seat in self.seats if seat.tier == tier), default=0)


def _row_strips(ring: Rect, offset: float, seats: SeatSpec) -> Iterator[tuple[Side, Rect]]:
    """Yield the four strips of floor for one row of chairs ``offset`` metres from the ring.

    Each strip stops ``corner_aisle_m`` short of the corner so a diagonal aisle runs out
    from every corner of the ring.
    """
    depth = seats.row_depth_m
    reach = offset - seats.corner_aisle_m
    across = ring.width + 2 * reach
    down = ring.height + 2 * reach
    if across <= 0 or down <= 0:
        return
    yield Side.TOP, Rect(ring.x - reach, ring.y - offset - depth, across, depth)
    yield Side.BOTTOM, Rect(ring.x - reach, ring.bottom + offset, across, depth)
    yield Side.LEFT, Rect(ring.x - offset - depth, ring.y - reach, depth, down)
    yield Side.RIGHT, Rect(ring.right + offset, ring.y - reach, depth, down)


def _blocks(
    start: float, end: float, splits: tuple[float, float], aisle: float
) -> list[tuple[float, float]]:
    """Split ``start..end`` into blocks, leaving an aisle centred on each split point.

    The splits line up with the ring's corners, so the aisles run straight back through
    every row.
    """
    edges = [start]
    for split in splits:
        if start < split < end:
            edges += [split - aisle / 2, split + aisle / 2]
    edges.append(end)
    return [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2)]


def _chairs_along(start: float, end: float, width: float) -> list[float]:
    """Positions of as many chairs as fit in ``start..end``, centred within it."""
    count = math.floor((end - start) / width + 1e-9)
    if count <= 0:
        return []
    first = start + ((end - start) - count * width) / 2
    return [first + i * width for i in range(count)]


def _strip_chairs(side: Side, strip: Rect, ring: Rect, seats: SeatSpec) -> Iterator[Rect]:
    horizontal = side in {Side.TOP, Side.BOTTOM}
    start, end = (strip.x, strip.right) if horizontal else (strip.y, strip.bottom)
    splits = (ring.x, ring.right) if horizontal else (ring.y, ring.bottom)
    for block_start, block_end in _blocks(start, end, splits, seats.radial_aisle_m):
        positions = _chairs_along(block_start, block_end, seats.width_m)
        if len(positions) < seats.min_block_seats:
            continue
        for pos in positions:
            if horizontal:
                yield Rect(pos, strip.y, seats.width_m, strip.height)
            else:
                yield Rect(strip.x, pos, strip.width, seats.width_m)


@dataclass(frozen=True)
class _Floor:
    ring: Rect
    seating_area: Rect
    keep_out: tuple[Rect, ...]
    seats: SeatSpec

    def row(self, tier: str, row: int, offset: float) -> list[Seat]:
        placed: list[Seat] = []
        for side, strip in _row_strips(self.ring, offset, self.seats):
            placed += [
                Seat(tier, row, side, chair)
                for chair in _strip_chairs(side, strip, self.ring, self.seats)
                if self.seating_area.contains(chair)
                and not any(chair.overlaps(zone) for zone in self.keep_out)
            ]
        return placed


def _place_tier(floor: _Floor, tier: TierSpec, offset: float) -> tuple[list[Seat], float]:
    """Place every row of ``tier`` starting ``offset`` metres out; return seats and new offset."""
    seats: list[Seat] = []
    row = 0
    while tier.rows is None or row < tier.rows:
        placed = floor.row(tier.name, row + 1, offset)
        if not placed:
            if tier.rows is None:
                break
            msg = f"tier {tier.name!r} row {row + 1} does not fit in the room"
            raise LayoutError(msg)
        seats += placed
        offset += floor.seats.row_depth_m
        row += 1
    return seats, offset


def build_layout(event: EventSpec) -> Layout:
    """Place the ring in the centre, the walkway and tunnel on the left, and seat every tier."""
    room = Rect(0, 0, event.room.width_m, event.room.depth_m)
    cx, cy = room.centre
    ring = Rect.centred(cx, cy, event.ring.platform_m, event.ring.platform_m)
    ropes = Rect.centred(cx, cy, event.ring.ropes_m, event.ring.ropes_m)
    walkway = Rect(0, cy - event.walkway.width_m / 2, ring.x, event.walkway.width_m)
    tunnel = Rect(0, cy - event.tunnel.width_m / 2, event.tunnel.depth_m, event.tunnel.width_m)
    floor = _Floor(
        ring=ring,
        seating_area=room.inset(event.room.perimeter_aisle_m),
        keep_out=(walkway.grow_vertically(event.walkway.barrier_m), tunnel),
        seats=event.seats,
    )
    seats: list[Seat] = []
    offset = event.ring.clearance_m
    for tier in event.tiers:
        placed, offset = _place_tier(floor, tier, offset + tier.gap_before_m)
        if not placed:
            msg = f"tier {tier.name!r} has no room for any seats"
            raise LayoutError(msg)
        seats += placed
    return Layout(
        event=event,
        room=room,
        seating_area=floor.seating_area,
        ring=ring,
        ropes=ropes,
        walkway=walkway,
        tunnel=tunnel,
        seats=tuple(seats),
    )
