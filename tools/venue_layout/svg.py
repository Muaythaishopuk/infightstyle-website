"""Render a :class:`~venue_layout.layout.Layout` as a scaled SVG floor plan."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from xml.sax.saxutils import escape

if TYPE_CHECKING:
    from venue_layout.geometry import Rect
    from venue_layout.layout import Layout

PX_PER_M = 24
MARGIN_PX = 56
LEGEND_PX = 300
FONT = "font-family='Helvetica, Arial, sans-serif'"
RED_CORNER = "#d62828"
BLUE_CORNER = "#1d4ed8"
NEUTRAL_CORNER = "#ffffff"


@dataclass(frozen=True)
class Style:
    """How a rectangle is painted."""

    fill: str
    stroke: str = "none"
    stroke_width: float = 0
    dash: str = ""
    radius: float = 0


def _px(metres: float) -> str:
    return f"{metres * PX_PER_M:.2f}"


def rect(area: Rect, style: Style) -> str:
    """An SVG ``<rect>`` for a rectangle measured in metres."""
    dash = f" stroke-dasharray='{style.dash}'" if style.dash else ""
    return (
        f"<rect x='{_px(area.x)}' y='{_px(area.y)}' width='{_px(area.width)}' "
        f"height='{_px(area.height)}' rx='{style.radius}' fill='{style.fill}' "
        f"stroke='{style.stroke}' stroke-width='{style.stroke_width}'{dash}/>"
    )


def text(x_px: float, y_px: float, label: str, *, size: int = 12, extra: str = "") -> str:
    """An SVG ``<text>`` placed in pixel coordinates."""
    return (
        f"<text x='{x_px:.2f}' y='{y_px:.2f}' font-size='{size}' {FONT} {extra}>"
        f"{escape(label)}</text>"
    )


def _centred_label(area: Rect, label: str, *, size: int, colour: str, rotate: bool = False) -> str:
    cx, cy = (float(_px(v)) for v in area.centre)
    turn = f" transform='rotate(-90 {cx:.2f} {cy:.2f})'" if rotate else ""
    extra = (
        f"text-anchor='middle' dominant-baseline='middle' fill='{colour}' font-weight='bold'{turn}"
    )
    return text(cx, cy, label, size=size, extra=extra)


def _grid(layout: Layout) -> list[str]:
    lines = []
    for metre in range(1, int(layout.room.width)):
        x = _px(metre)
        lines.append(f"<line x1='{x}' y1='0' x2='{x}' y2='{_px(layout.room.height)}'/>")
    for metre in range(1, int(layout.room.height)):
        y = _px(metre)
        lines.append(f"<line x1='0' y1='{y}' x2='{_px(layout.room.width)}' y2='{y}'/>")
    return ["<g stroke='#e5e7eb' stroke-width='0.5'>", *lines, "</g>"]


def _ring(layout: Layout) -> list[str]:
    ring, ropes = layout.ring, layout.ropes
    post = 0.3
    corners = [
        (ropes.x, ropes.y, RED_CORNER),
        (ropes.right, ropes.bottom, BLUE_CORNER),
        (ropes.right, ropes.y, NEUTRAL_CORNER),
        (ropes.x, ropes.bottom, NEUTRAL_CORNER),
    ]
    parts = [
        rect(ring, Style("#374151", "#111827", 2)),
        rect(ropes, Style("#f3f4f6", "#b91c1c", 3)),
    ]
    for x, y, colour in corners:
        cx, cy = _px(x), _px(y)
        parts.append(
            f"<circle cx='{cx}' cy='{cy}' r='{post * PX_PER_M:.2f}' fill='{colour}' "
            "stroke='#111827' stroke-width='1.5'/>"
        )
    parts.append(_centred_label(ropes, "RING", size=22, colour="#111827"))
    return parts


def _walkout(layout: Layout) -> list[str]:
    walkway, tunnel = layout.walkway, layout.tunnel
    barrier = layout.event.walkway.barrier_m
    return [
        rect(walkway.grow_vertically(barrier), Style("#fde68a")),
        rect(walkway, Style("#111827")),
        rect(tunnel, Style("#000000", "#facc15", 2)),
        _centred_label(walkway, "FIGHTER WALKWAY", size=11, colour="#facc15"),
        _centred_label(tunnel, "TUNNEL", size=10, colour="#facc15", rotate=True),
    ]


def _seats(layout: Layout) -> list[str]:
    colours = {tier.name: tier.colour for tier in layout.event.tiers}
    return [
        rect(seat.rect.inset(0.04), Style(colours[seat.tier], "#1f2937", 0.4, radius=2))
        for seat in layout.seats
    ]


def _dimensions(layout: Layout) -> list[str]:
    width, height = layout.room.width, layout.room.height
    mid_x, mid_y = float(_px(width / 2)), float(_px(height / 2))
    side_x = -22.0
    return [
        text(mid_x, -16, f"{width:g} m", size=14, extra="text-anchor='middle' font-weight='bold'"),
        text(
            side_x,
            mid_y,
            f"{height:g} m",
            size=14,
            extra=(
                "text-anchor='middle' font-weight='bold' "
                f"transform='rotate(-90 {side_x} {mid_y:.2f})'"
            ),
        ),
    ]


def _legend(layout: Layout, left_px: float) -> list[str]:
    event = layout.event
    parts = [
        text(left_px, 18, event.title, size=18, extra="font-weight='bold'"),
        text(left_px, 40, event.date, size=13, extra="fill='#4b5563'"),
        text(left_px, 78, "Seating tiers", size=14, extra="font-weight='bold'"),
    ]
    y = 100.0
    for tier in event.tiers:
        parts.append(
            f"<rect x='{left_px:.2f}' y='{y - 11:.2f}' width='16' height='16' rx='3' "
            f"fill='{tier.colour}' stroke='#1f2937' stroke-width='0.6'/>"
        )
        summary = f"{tier.name}: {layout.count(tier.name)} seats, {layout.rows(tier.name)} rows"
        parts.append(text(left_px + 24, y + 2, summary, size=13))
        y += 26
    parts.append(
        text(
            left_px, y + 4, f"Total: {len(layout.seats)} seats", size=14, extra="font-weight='bold'"
        )
    )
    notes = [
        f"Ring platform {event.ring.platform_m:g} m, ropes {event.ring.ropes_m:g} m",
        f"{event.ring.clearance_m:g} m clear around ring (officials, corners)",
        f"Walkway {event.walkway.width_m:g} m wide + {event.walkway.barrier_m:g} m barriers",
        f"{event.room.perimeter_aisle_m:g} m aisle round the walls",
        f"{event.seats.corner_aisle_m:g} m diagonal aisles at the corners",
        f"{event.seats.radial_aisle_m:g} m aisles in line with the ring posts",
        f"Chair {event.seats.width_m:g} m wide, rows {event.seats.row_depth_m:g} m deep",
        "Red corner top-left, blue corner bottom-right",
        "Grid squares are 1 m",
    ]
    y += 44
    parts.append(text(left_px, y, "Notes", size=14, extra="font-weight='bold'"))
    for note in notes:
        y += 20
        parts.append(text(left_px, y, note, size=11, extra="fill='#374151'"))
    return parts


def render_svg(layout: Layout) -> str:
    """Return the complete SVG document for ``layout``."""
    room = layout.room
    plan_w = float(_px(room.width))
    plan_h = float(_px(room.height))
    width = plan_w + 2 * MARGIN_PX + LEGEND_PX
    height = plan_h + 2 * MARGIN_PX
    body = [
        rect(room, Style("#ffffff", "#111827", 3)),
        *_grid(layout),
        rect(layout.seating_area, Style("none", "#9ca3af", 1, dash="6 4")),
        *_walkout(layout),
        *_seats(layout),
        *_ring(layout),
        *_dimensions(layout),
        *_legend(layout, plan_w + 32),
    ]
    return "\n".join(
        [
            "<?xml version='1.0' encoding='UTF-8'?>",
            (
                f"<svg xmlns='http://www.w3.org/2000/svg' width='{width:.0f}' "
                f"height='{height:.0f}' viewBox='0 0 {width:.0f} {height:.0f}'>"
            ),
            f"<rect width='{width:.0f}' height='{height:.0f}' fill='#f9fafb'/>",
            f"<g transform='translate({MARGIN_PX} {MARGIN_PX})'>",
            *body,
            "</g>",
            "</svg>",
            "",
        ]
    )
