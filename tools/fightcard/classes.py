"""Fight classes: reading them from the sheet, their order and their slot length."""

from __future__ import annotations

import re
from dataclasses import dataclass

_CLASS_PATTERN = re.compile(r"^\s*([a-z])\s+class\b", re.IGNORECASE)


class UnknownClassError(ValueError):
    """Raised when a class written in the sheet is not in the event's class list."""


@dataclass(frozen=True)
class FightClass:
    """A class of bout, such as "N Class", with how long its slot lasts."""

    code: str
    label: str
    minutes: int


def parse_class_code(text: str) -> str | None:
    """Return the class letter from text such as " c class pro ", or None if absent."""
    match = _CLASS_PATTERN.match(text)
    return match.group(1).upper() if match else None


def class_by_code(classes: tuple[FightClass, ...], code: str) -> FightClass:
    """Find a class by its letter, or raise UnknownClassError."""
    for fight_class in classes:
        if fight_class.code == code:
            return fight_class
    known = ", ".join(c.code for c in classes)
    msg = f"Class {code!r} is not one of the event's classes ({known})."
    raise UnknownClassError(msg)
