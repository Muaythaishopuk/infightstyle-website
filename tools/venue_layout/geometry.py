"""Axis-aligned rectangles measured in metres, with the origin at the room's top-left corner."""

from __future__ import annotations

import math
from dataclasses import dataclass

_EPSILON = 1e-9


def whole_fits(length: float, size: float) -> int:
    """How many items of ``size`` fit in ``length``, ignoring floating-point dust."""
    return max(math.floor(length / size + _EPSILON), 0)


@dataclass(frozen=True)
class Rect:
    """A rectangle; ``x`` grows to the right and ``y`` grows down the page."""

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        """Reject rectangles with negative size."""
        if self.width < 0 or self.height < 0:
            msg = f"Rect size must not be negative, got {self.width} x {self.height}"
            raise ValueError(msg)

    @classmethod
    def centred(cls, cx: float, cy: float, width: float, height: float) -> Rect:
        """Build a rectangle centred on ``(cx, cy)``."""
        return cls(cx - width / 2, cy - height / 2, width, height)

    @property
    def right(self) -> float:
        """The x coordinate of the right edge."""
        return self.x + self.width

    @property
    def bottom(self) -> float:
        """The y coordinate of the bottom edge."""
        return self.y + self.height

    @property
    def centre(self) -> tuple[float, float]:
        """The centre point."""
        return (self.x + self.width / 2, self.y + self.height / 2)

    def overlaps(self, other: Rect) -> bool:
        """Return True if the interiors intersect (touching edges do not count)."""
        return (
            self.x < other.right - _EPSILON
            and other.x < self.right - _EPSILON
            and self.y < other.bottom - _EPSILON
            and other.y < self.bottom - _EPSILON
        )

    def contains(self, other: Rect) -> bool:
        """Return True if ``other`` lies entirely inside this rectangle."""
        return (
            other.x >= self.x - _EPSILON
            and other.y >= self.y - _EPSILON
            and other.right <= self.right + _EPSILON
            and other.bottom <= self.bottom + _EPSILON
        )

    def inset(self, margin: float) -> Rect:
        """Shrink by ``margin`` on every side (a negative margin grows it)."""
        return Rect(
            self.x + margin,
            self.y + margin,
            max(self.width - 2 * margin, 0.0),
            max(self.height - 2 * margin, 0.0),
        )

    def grow_vertically(self, margin: float) -> Rect:
        """Grow by ``margin`` above and below."""
        return Rect(self.x, self.y - margin, self.width, self.height + 2 * margin)
