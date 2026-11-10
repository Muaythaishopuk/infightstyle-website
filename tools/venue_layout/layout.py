"""Work out where the ring, walkway, tunnel, bleachers and every floor chair go."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from venue_layout.config import Side
from venue_layout.geometry import Rect, whole_fits

if TYPE_CHECKING:
    from collections.abc import Iterator

    from venue_layout.config import EventSpec, SeatSpec, TierSpec


class LayoutError(ValueError):
    """Raised when the requested tiers cannot physically fit in the room."""


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
    bleachers: tuple[Rect, ...]
    bleacher_capacity: int
    seats: tuple[Seat, ...]

    def count(self, tier: str) -> int:
        """Number of floor chairs in ``tier``."""
        return sum(1 for seat in self.seats if seat.tier == tier)

    def rows(self, tier: str) -> int:
        """Deepest row number used by ``tier`` (0 if it has no seats)."""
        return max((seat.row for seat in self.seats if seat.tier == tier), default=0)


def _strip(side: Side, ring: Rect, offset: float, seats: SeatSpec) -> Rect | None:
    """The strip of floor for one row on ``side``, ``offset`` metres out from the ring.

    The strip stops ``corner_aisle_m`` short of each corner so a diagonal aisle runs out
    from every corner of the ring.
    """
    depth = seats.row_depth_m
    reach = offset - seats.corner_aisle_m
    length = ring.width + 2 * reach
    if length <= 0:
        return None
    return {
        Side.TOP: Rect(ring.x - reach, ring.y - offset - depth, length, depth),
        Side.BOTTOM: Rect(ring.x - reach, ring.bottom + offset, length, depth),
        Side.LEFT: Rect(ring.x - offset - depth, ring.y - reach, depth, length),
        Side.RIGHT: Rect(ring.right + offset, ring.y - reach, depth, length),
    }[side]


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
    count = whole_fits(end - start, width)
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


def _best_first(row: list[Seat], ring: Rect) -> list[Seat]:
    """Order a row so any prefix of it is spread evenly over the sides, centre seats first.

    Seats are dealt round-robin from each side, nearest the middle of that side first, so
    trimming the last row of a tier leaves a tidy centred block on every side.
    """
    cx, cy = ring.centre

    def off_centre(seat: Seat) -> tuple[float, float, float]:
        sx, sy = seat.rect.centre
        along = sx - cx if seat.side in {Side.TOP, Side.BOTTOM} else sy - cy
        return (round(abs(along), 6), sx, sy)

    by_side = [sorted((s for s in row if s.side == side), key=off_centre) for side in Side]
    longest = max(map(len, by_side), default=0)
    return [queue[i] for i in range(longest) for queue in by_side if i < len(queue)]


@dataclass
class _Floor:
    """Mutable placement state: what is placed so far and how deep each side has got."""

    ring: Rect
    seating_area: Rect
    keep_out: tuple[Rect, ...]
    seats: SeatSpec
    depth: dict[Side, float]
    placed: list[Seat]

    def _free(self, chair: Rect, tier: TierSpec) -> bool:
        if not self.seating_area.contains(chair):
            return False
        if any(chair.overlaps(zone) for zone in self.keep_out):
            return False
        return not any(
            chair.overlaps(
                seat.rect if seat.tier == tier.name else seat.rect.inset(-tier.gap_before_m)
            )
            for seat in self.placed
        )

    def row(self, tier: TierSpec, row: int) -> list[Seat]:
        """Chairs for one row of ``tier`` on each of its sides, then step those sides out."""
        found: list[Seat] = []
        for side in tier.sides:
            strip = _strip(side, self.ring, self.depth[side], self.seats)
            if strip is not None:
                found += [
                    Seat(tier.name, row, side, chair)
                    for chair in _strip_chairs(side, strip, self.ring, self.seats)
                    if self._free(chair, tier)
                ]
            self.depth[side] += self.seats.row_depth_m
        return found

    def place(self, tier: TierSpec) -> None:
        """Add rows for ``tier`` until its target, row limit or the walls are reached."""
        for side in tier.sides:
            self.depth[side] += tier.gap_before_m
        total = 0
        row = 0
        while tier.rows is None or row < tier.rows:
            row += 1
            found = _best_first(self.row(tier, row), self.ring)
            if not found:
                break
            if tier.target_seats is not None:
                found = found[: tier.target_seats - total]
            self.placed += found
            total += len(found)
            if total == tier.target_seats:
                return
        if tier.target_seats is not None or total == 0:
            wanted = tier.target_seats or 1
            msg = f"tier {tier.name!r} only fits {total} of {wanted} seats"
            raise LayoutError(msg)


def _bleachers(event: EventSpec, tunnel: Rect, room: Rect) -> tuple[Rect, Rect]:
    """The stand against the left wall, split in two by the tunnel."""
    spec = event.bleachers
    stand = Rect.centred(spec.depth_m / 2, room.centre[1], spec.depth_m, spec.length_m)
    return (
        Rect(stand.x, stand.y, stand.width, tunnel.y - stand.y),
        Rect(stand.x, tunnel.bottom, stand.width, stand.bottom - tunnel.bottom),
    )


def _bleacher_capacity(event: EventSpec, halves: tuple[Rect, Rect]) -> int:
    """Rough capacity: whole rows times whole seats per row, in both halves."""
    spec = event.bleachers
    return sum(spec.steps * whole_fits(half.height, spec.seat_width_m) for half in halves)


def build_layout(event: EventSpec) -> Layout:
    """Place the ring in the centre, walkway, tunnel and bleachers on the left, then seat tiers."""
    room = Rect(0, 0, event.room.width_m, event.room.depth_m)
    cx, cy = room.centre
    ring = Rect.centred(cx, cy, event.ring.platform_m, event.ring.platform_m)
    walkway = Rect(0, cy - event.walkway.width_m / 2, ring.x, event.walkway.width_m)
    tunnel = Rect(0, cy - event.tunnel.width_m / 2, event.tunnel.depth_m, event.tunnel.width_m)
    bleachers = _bleachers(event, tunnel, room)
    aisle = event.room.perimeter_aisle_m
    floor_left = event.bleachers.depth_m + aisle
    floor = _Floor(
        ring=ring,
        seating_area=Rect(
            floor_left, aisle, room.width - floor_left - aisle, room.height - 2 * aisle
        ),
        keep_out=(walkway.grow_vertically(event.walkway.barrier_m), tunnel),
        seats=event.seats,
        depth=dict.fromkeys(Side, event.ring.clearance_m),
        placed=[],
    )
    for tier in event.tiers:
        floor.place(tier)
    return Layout(
        event=event,
        room=room,
        seating_area=floor.seating_area,
        ring=ring,
        ropes=Rect.centred(cx, cy, event.ring.ropes_m, event.ring.ropes_m),
        walkway=walkway,
        tunnel=tunnel,
        bleachers=bleachers,
        bleacher_capacity=_bleacher_capacity(event, bleachers),
        seats=tuple(floor.placed),
    )
