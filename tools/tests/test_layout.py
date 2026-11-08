import itertools

import pytest

from tests.conftest import event_with
from venue_layout.config import EventSpec
from venue_layout.layout import Layout, LayoutError, Side, build_layout


@pytest.fixture
def layout(event: EventSpec) -> Layout:
    return build_layout(event)


def test_ring_is_centred(layout: Layout) -> None:
    assert layout.ring.centre == layout.room.centre
    assert layout.ropes.centre == layout.room.centre
    assert layout.ring.contains(layout.ropes)


def test_walkway_runs_from_left_wall_to_middle_of_ring(layout: Layout) -> None:
    assert layout.walkway.x == 0
    assert layout.walkway.right == layout.ring.x
    assert layout.walkway.centre[1] == layout.ring.centre[1]
    assert layout.tunnel.x == 0
    assert layout.tunnel.centre[1] == layout.ring.centre[1]


def test_seats_stay_inside_the_aisle_round_the_walls(layout: Layout) -> None:
    assert all(layout.seating_area.contains(seat.rect) for seat in layout.seats)


def test_no_seat_blocks_ring_walkway_or_tunnel(layout: Layout) -> None:
    barrier = layout.event.walkway.barrier_m
    blocked = [layout.ring, layout.walkway.grow_vertically(barrier), layout.tunnel]
    assert not any(seat.rect.overlaps(zone) for seat in layout.seats for zone in blocked)


def test_no_two_seats_overlap(layout: Layout) -> None:
    pairs = itertools.combinations(layout.seats, 2)
    assert not any(a.rect.overlaps(b.rect) for a, b in pairs)


def test_tiers_get_further_from_ring(layout: Layout) -> None:
    def nearest(tier: str) -> float:
        cx, cy = layout.ring.centre
        return min(
            max(abs(s.rect.centre[0] - cx), abs(s.rect.centre[1] - cy))
            for s in layout.seats
            if s.tier == tier
        )

    distances = [nearest(tier.name) for tier in layout.event.tiers]
    assert distances == sorted(distances)
    first_row = layout.ring.width / 2 + layout.event.ring.clearance_m
    assert distances[0] > first_row


def test_fixed_rows_and_fill(layout: Layout) -> None:
    assert layout.rows("Ringside") == 2
    assert layout.rows("Outer ringside") == 2
    assert layout.rows("Standard") >= 2
    assert layout.rows("Nobody") == 0


def test_every_side_has_seats(layout: Layout) -> None:
    assert {seat.side for seat in layout.seats} == set(Side)


def test_seat_counts_are_stable(layout: Layout) -> None:
    counts = [layout.count(tier.name) for tier in layout.event.tiers]
    assert counts == [74, 170, 309]
    assert sum(counts) == len(layout.seats)


def test_small_fragments_are_dropped() -> None:
    assert len(build_layout(event_with("seats", "min_block_seats", 1)).seats) > 553


def test_too_many_fixed_rows_raises() -> None:
    with pytest.raises(LayoutError, match="'Outer ringside' row 7 does not fit"):
        build_layout(event_with("tiers[1]", "rows", 40))


def test_fill_tier_with_no_space_raises() -> None:
    with pytest.raises(LayoutError, match="'Standard' has no room"):
        build_layout(event_with("tiers[1]", "rows", 6))


def test_huge_corner_aisle_leaves_no_front_row() -> None:
    with pytest.raises(LayoutError, match="'Ringside' row 1 does not fit"):
        build_layout(event_with("seats", "corner_aisle_m", 6))
