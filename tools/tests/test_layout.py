import itertools

import pytest

from tests.conftest import event_data, event_with, tier
from venue_layout.config import EventSpec, Side, parse_event
from venue_layout.layout import Layout, LayoutError, Seat, _runs, build_layout


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


def test_no_seat_blocks_ring_walkway_tunnel_or_bleachers(layout: Layout) -> None:
    barrier = layout.event.walkway.barrier_m
    blocked = [layout.ring, layout.walkway.grow_vertically(barrier), layout.tunnel]
    blocked += layout.bleachers
    assert not any(seat.rect.overlaps(zone) for seat in layout.seats for zone in blocked)


def test_no_two_seats_overlap(layout: Layout) -> None:
    pairs = itertools.combinations(layout.seats, 2)
    assert not any(a.rect.overlaps(b.rect) for a, b in pairs)


def test_outer_ringside_is_behind_ringside(layout: Layout) -> None:
    cx, cy = layout.ring.centre

    def nearest(tier: str) -> float:
        return min(
            max(abs(s.rect.centre[0] - cx), abs(s.rect.centre[1] - cy))
            for s in layout.seats
            if s.tier == tier
        )

    first_row = layout.ring.width / 2 + layout.event.ring.clearance_m
    assert first_row < nearest("Ringside") < nearest("Outer ringside")


def test_targets_are_hit_exactly(layout: Layout) -> None:
    assert layout.count("Ringside") == 150
    assert layout.count("Outer ringside") == 200
    assert layout.count("Standard") == 150
    assert layout.rows("Nobody") == 0


def test_tiers_only_use_their_sides(layout: Layout) -> None:
    for spec in layout.event.tiers:
        used = {seat.side for seat in layout.seats if seat.tier == spec.name}
        assert used <= set(spec.sides)
    assert {s.side for s in layout.seats if s.tier == "Standard"} == {Side.LEFT}
    assert Side.LEFT not in {s.side for s in layout.seats if s.tier != "Standard"}


def test_standard_sits_between_bleachers_and_ring(layout: Layout) -> None:
    standard = [s.rect for s in layout.seats if s.tier == "Standard"]
    bleacher_front = layout.bleachers[0].right
    assert all(bleacher_front < seat.x and seat.right < layout.ring.x for seat in standard)


def test_tunnel_splits_bleachers(layout: Layout) -> None:
    top, bottom = layout.bleachers
    assert top.bottom == layout.tunnel.y
    assert bottom.y == layout.tunnel.bottom
    assert top.x == 0
    # 6 steps x (11.3 m / 0.45 m = 25 seats) x 2 halves
    assert layout.bleacher_capacity == 300


def test_partial_last_row_is_spread_over_sides(layout: Layout) -> None:
    last = layout.rows("Ringside")
    sides = [s.side for s in layout.seats if s.tier == "Ringside" and s.row == last]
    used = layout.event.tiers[1].sides
    assert set(sides) == set(used)
    assert max(map(sides.count, used)) - min(map(sides.count, used)) <= 1


def test_seat_counts_are_stable(layout: Layout) -> None:
    counts = [layout.count(tier.name) for tier in layout.event.tiers]
    assert counts == [150, 150, 200]
    assert sum(counts) == len(layout.seats)


def test_small_fragments_are_dropped(layout: Layout) -> None:
    def group(seat: Seat) -> tuple[str, int, str]:
        return (seat.tier, seat.row, seat.side.value)

    ordered = sorted(layout.seats, key=lambda s: (*group(s), s.rect.x, s.rect.y))
    width = layout.event.seats.width_m
    for _, seats in itertools.groupby(ordered, key=group):
        for run in _runs([s.rect for s in seats], width):
            assert len(run) >= layout.event.seats.min_block_seats
    with pytest.raises(LayoutError, match="'Standard' only fits 136"):
        build_layout(event_with("seats", "min_block_seats", 3))


def test_tiers_keep_an_aisle_between_them(layout: Layout) -> None:
    aisle = layout.event.seats.tier_aisle_m
    for a, b in itertools.combinations(layout.seats, 2):
        if a.tier != b.tier:
            assert not a.rect.inset(-aisle).overlaps(b.rect)


def test_straight_rows_run_full_height(layout: Layout) -> None:
    standard = [s.rect for s in layout.seats if s.tier == "Standard"]
    assert min(r.y for r in standard) < layout.ring.y - 6
    assert max(r.bottom for r in standard) > layout.ring.bottom + 6


def test_row_limit_stops_a_tier() -> None:
    limited = build_layout(event_with("tiers[2]", "target_seats", None))
    assert limited.count("Outer ringside") > 200
    data = event_data()
    tier(data, 0).update(rows=1, target_seats=None)
    assert build_layout(parse_event(data)).rows("Standard") == 1


def test_target_too_big_raises() -> None:
    with pytest.raises(LayoutError, match=r"'Outer ringside' only fits \d+ of 2000"):
        build_layout(event_with("tiers[2]", "target_seats", 2000))


def test_target_beyond_row_limit_raises() -> None:
    with pytest.raises(LayoutError, match=r"'Ringside' only fits \d+ of 150"):
        build_layout(event_with("tiers[1]", "rows", 1))


def test_fill_tier_with_no_space_raises() -> None:
    with pytest.raises(LayoutError, match="'Standard' only fits 0 of 1"):
        build_layout(event_with("tiers[0]", "gap_before_m", 10))


def test_huge_corner_aisle_leaves_no_front_row() -> None:
    with pytest.raises(LayoutError, match="'Ringside' only fits 0 of 150"):
        build_layout(event_with("seats", "corner_aisle_m", 9))
