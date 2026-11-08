# INFIGHTSTYLE planning tools

## Venue floor plans (`venue_layout`)

Draws a to-scale floor plan for a fight night from a small settings file: the ring in
the centre, the fighters' walkway from the middle of the ring's left side to the tunnel on
the left wall, and seating tiers in rings around the ring (closest tier first).

```bash
cd tools
python -m venue_layout ../planning/2026-11-21-fight-league-1/event.json
```

This writes `layout.svg` next to the settings file and prints the seat count per tier.
Running it again with no changes leaves the file untouched.

### Changing the plan

Edit the event's `event.json`, then run the command again. All sizes are in metres.

| Setting | Meaning |
|---|---|
| `room.width_m` / `depth_m` | Room size: width runs left to right (walkway direction) |
| `room.perimeter_aisle_m` | Clear aisle kept free round all four walls |
| `ring.platform_m` / `ropes_m` | Outer platform size and inside-the-ropes size |
| `ring.clearance_m` | Clear floor between the platform and the first row (officials, corners, steps) |
| `walkway.width_m` / `barrier_m` | Walkway width, plus space for a barrier each side |
| `tunnel.width_m` / `depth_m` | Tunnel opening and how far it comes into the room |
| `seats.width_m` / `row_depth_m` | Space per chair and per row |
| `seats.corner_aisle_m` | Diagonal aisle out from each ring corner |
| `seats.radial_aisle_m` | Aisles lined up with the ring posts, cutting through every row |
| `seats.min_block_seats` | Leave out blocks smaller than this (avoids lone chairs) |
| `tiers[]` | Closest to the ring first. `rows` is a number, or `null` on the last tier to fill the rest. `gap_before_m` is a walking aisle before that tier |

For a new event, copy the folder under `planning/`, rename it and edit `event.json`.

## Quality checks

```bash
cd tools
pip install -e ".[dev]"
python check.py
```

Runs formatting (ruff), linting (ruff, every rule on), strict type checks (mypy),
tests with at least 95% coverage (pytest), and copy-paste detection (jscpd, zero
duplication allowed). All must pass before changes are committed.
