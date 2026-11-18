"""Values written into Google Sheets cells."""

from __future__ import annotations

Cell = str | int | float


def as_text(value: str) -> str:
    """Stop Sheets reading names such as "2 tech" or "1-1" as numbers or dates."""
    return f"'{value}"
