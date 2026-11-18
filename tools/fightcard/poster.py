"""The public running-order post: fighter names only, main and co-main event first.

Bouts are listed from the last of the night to the first. The first ``featured`` bouts are
drawn larger, each with a label such as "MAIN EVENT". The background image sets the size.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

    from fightcard.schedule import Slot

WHITE = (255, 255, 255)
RED = (225, 30, 36)
GREY = (200, 200, 200)
OUTLINE = (0, 0, 0)
VS = "VS"


@dataclass(frozen=True)
class PosterLine:
    """One bout on the post."""

    red: str
    blue: str
    label: str | None


@dataclass(frozen=True)
class PosterStyle:
    """Fonts, wording and the vertical layout, in pixels of the background image."""

    font: Path
    title: str
    subtitle: str
    labels: tuple[str, ...] = ("MAIN EVENT", "CO-MAIN EVENT")
    margin: int = 110
    title_top: int = 250
    title_size: int = 120
    subtitle_size: int = 44
    featured_size: int = 74
    label_size: int = 34
    line_size: int = 40
    bottom: int = 70
    outline: int = 2


def poster_lines(slots: Sequence[Slot], labels: Sequence[str]) -> list[PosterLine]:
    """Bouts from last to first; the first ``len(labels)`` get those labels."""
    bouts = [slot.bout for slot in reversed(slots) if slot.bout is not None]
    return [
        PosterLine(
            red=bout.red.name.strip().upper(),
            blue=bout.blue.name.strip().upper(),
            label=labels[index] if index < len(labels) else None,
        )
        for index, bout in enumerate(bouts)
    ]


def fit_size(width_at: Callable[[int], float], max_width: int, size: int) -> int:
    """Largest size, at most ``size``, whose text is no wider than ``max_width``."""
    while size > 1 and width_at(size) > max_width:
        size -= 1
    return size


class _Canvas:
    def __init__(self, image: Image.Image, style: PosterStyle) -> None:
        self.draw = ImageDraw.Draw(image)
        self.style = style
        self.width = image.width

    def font(self, size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(self.style.font), size)

    def text_width(self, text: str, size: int) -> float:
        return self.draw.textlength(text, font=self.font(size))

    def centred(self, text: str, top: int, size: int, colour: tuple[int, int, int]) -> int:
        size = fit_size(
            lambda s: self.text_width(text, s), self.width - 2 * self.style.margin, size
        )
        font = self.font(size)
        self._text((self.width / 2, top), text, font, colour, "mt")
        return top + size

    def bout(self, line: PosterLine, top: int, size: int) -> None:
        half = self.width / 2
        gap = self.text_width(VS, size) / 2 + size * 0.45
        room = half - gap - self.style.margin
        widest = max(line.red, line.blue, key=lambda name: self.text_width(name, size))
        size = fit_size(lambda s: self.text_width(widest, s), int(room), size)
        font = self.font(size)
        self._text((half - gap, top), line.red, font, WHITE, "rm")
        self._text((half, top), VS, font, RED, "mm")
        self._text((half + gap, top), line.blue, font, WHITE, "lm")

    def _text(
        self,
        xy: tuple[float, float],
        text: str,
        font: ImageFont.FreeTypeFont,
        colour: tuple[int, int, int],
        anchor: str,
    ) -> None:
        self.draw.text(
            xy,
            text,
            font=font,
            fill=colour,
            anchor=anchor,
            stroke_width=self.style.outline,
            stroke_fill=OUTLINE,
        )


def render(lines: Sequence[PosterLine], background: Path, out: Path, style: PosterStyle) -> None:
    """Draw the post onto the background and save it to ``out``."""
    with Image.open(background) as source:
        image = source.convert("RGBA")
    canvas = _Canvas(image, style)
    top = canvas.centred(style.title, style.title_top, style.title_size, WHITE) + 24
    top = canvas.centred(style.subtitle, top, style.subtitle_size, GREY) + 50

    featured = [line for line in lines if line.label]
    rest = [line for line in lines if not line.label]
    for line in featured:
        top = canvas.centred(line.label or "", top, style.label_size, RED) + 18
        canvas.bout(line, top + style.featured_size // 2, style.featured_size)
        top += style.featured_size + 44

    list_top = top + 10
    step = (image.height - style.bottom - list_top) / max(len(rest), 1)
    for index, line in enumerate(rest):
        canvas.bout(line, int(list_top + step * (index + 0.5)), style.line_size)
    image.convert("RGB").save(out, quality=95)
