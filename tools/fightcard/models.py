"""Plain data types shared by every module."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum

TBC = "TBC"


class Corner(Enum):
    """The two corners of the ring."""

    RED = "red"
    BLUE = "blue"

    @property
    def other(self) -> Corner:
        """Return the opposite corner."""
        return Corner.BLUE if self is Corner.RED else Corner.RED


@dataclass(frozen=True)
class Fighter:
    """One fighter and the gym they represent."""

    name: str
    gym: str


@dataclass(frozen=True)
class Bout:
    """One fight. ``red`` and ``blue`` are the corners as currently assigned."""

    red: Fighter
    blue: Fighter
    fight_class: str
    source: str

    def swapped(self) -> Bout:
        """Return the same bout with the corners exchanged."""
        return replace(self, red=self.blue, blue=self.red)


@dataclass
class BoutsResult:
    """Bouts from one processing step, plus anything a person should check."""

    bouts: list[Bout] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
