"""The public running-order post: fighter names only, from the main event down to fight 1.

Three levels, each drawn smaller than the one before:

- headliners (main and co-main event), each under a red banner naming the title at stake;
- the rest of the main card (the classes named in ``main_card_classes``);
- the undercard.

The background image sets the size of the post.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from collections.abc import Callable, Collection, Sequence
    from pathlib import Path

    from fightcard.schedule import Slot

Colour = tuple[int, int, int]
WHITE: Colour = (255, 255, 255)
RED: Colour = (225, 30, 36)
GOLD: Colour = (245, 196, 66)
GREY: Colour = (205, 205, 205)
OUTLINE: Colour = (0, 0, 0)
VS = "VS"
BANNER_DIVIDER = "  •  "


class Tier(Enum):
    """How prominent a bout is on the post."""

    HEADLINE = "headline"
    MAIN_CARD = "main card"
    UNDERCARD = "undercard"


@dataclass(frozen=True)
class Headliner:
    """The banner over a headline bout, such as MAIN EVENT and WMO WORLD TITLE."""

    label: str
    title: str


@dataclass(frozen=True)
class PosterLine:
    """One bout on the post."""

    red: str
    blue: str
    tier: Tier
    headliner: Headliner | None = None


@dataclass(frozen=True)
class PosterStyle:
    """Font, wording and sizes, in pixels of the background image."""

    font: Path
    title: str
    subtitle: str
    margin: int = 100
    headline_margin: int = 45
    title_top: int = 225
    title_size: int = 96
    subtitle_size: int = 38
    banner_size: int = 34
    headline_sizes: tuple[int, ...] = (110, 92)
    section_size: int = 40
    main_card_size: int = 46
    undercard_size: int = 34
    bottom: int = 60
    outline: int = 2


def poster_lines(
    slots: Sequence[Slot], headliners: Sequence[Headliner], main_card_classes: Collection[str]
) -> list[PosterLine]:
    """Bouts from last to first, sorted into headliners, main card and undercard."""
    bouts = [slot.bout for slot in reversed(slots) if slot.bout is not None]
    lines: list[PosterLine] = []
    for index, bout in enumerate(bouts):
        red, blue = bout.red.name.strip().upper(), bout.blue.name.strip().upper()
        if index < len(headliners):
            lines.append(PosterLine(red, blue, Tier.HEADLINE, headliners[index]))
        elif bout.fight_class in main_card_classes:
            lines.append(PosterLine(red, blue, Tier.MAIN_CARD))
        else:
            lines.append(PosterLine(red, blue, Tier.UNDERCARD))
    return lines


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

    def text(
        self, xy: tuple[float, float], text: str, size: int, colour: Colour, anchor: str
    ) -> None:
        self.draw.text(
            xy,
            text,
            font=self.font(size),
            fill=colour,
            anchor=anchor,
            stroke_width=self.style.outline,
            stroke_fill=OUTLINE,
        )

    def centred(self, text: str, top: int, size: int, colour: Colour) -> int:
        size = fit_size(
            lambda s: self.text_width(text, s), self.width - 2 * self.style.margin, size
        )
        self.text((self.width / 2, top), text, size, colour, "mt")
        return top + size

    def bout(self, line: PosterLine, middle: int, size: int, margin: int | None = None) -> None:
        half = self.width / 2
        gap = self.text_width(VS, size) / 2 + size * 0.45
        room = int(half - gap - (self.style.margin if margin is None else margin))
        widest = max(line.red, line.blue, key=lambda name: self.text_width(name, size))
        size = fit_size(lambda s: self.text_width(widest, s), room, size)
        gap = self.text_width(VS, size) / 2 + size * 0.45
        self.text((half - gap, middle), line.red, size, WHITE, "rm")
        self.text((half, middle), VS, size, RED, "mm")
        self.text((half + gap, middle), line.blue, size, WHITE, "lm")

    def banner(self, headliner: Headliner, top: int) -> int:
        """Draw a slanted red banner with the label in white and the title in gold."""
        size = self.style.banner_size
        label, title = headliner.label + BANNER_DIVIDER, headliner.title
        text_width = self.text_width(label, size) + self.text_width(title, size)
        height = int(size * 1.7)
        pad, skew = size * 1.2, height * 0.45
        left, right = (self.width - text_width) / 2 - pad, (self.width + text_width) / 2 + pad
        self.draw.polygon(
            [
                (left + skew, top),
                (right + skew, top),
                (right - skew, top + height),
                (left - skew, top + height),
            ],
            fill=RED,
        )
        middle, start = top + height / 2, (self.width - text_width) / 2
        self.text((start, middle), label, size, WHITE, "lm")
        self.text((start + self.text_width(label, size), middle), title, size, GOLD, "lm")
        return top + height

    def section(self, heading: str, top: int) -> int:
        """Draw a heading with a rule either side, such as --- MAIN CARD ---."""
        size = self.style.section_size
        half_text = self.text_width(heading, size) / 2
        middle, half = top + size / 2, self.width / 2
        for start, end in (
            (self.style.margin, half - half_text - 30),
            (half + half_text + 30, self.width - self.style.margin),
        ):
            self.draw.line([(start, middle), (end, middle)], fill=RED, width=4)
        self.text((half, middle), heading, size, RED, "mm")
        return top + size


def _rows(lines: Sequence[PosterLine], tier: Tier) -> list[PosterLine]:
    return [line for line in lines if line.tier is tier]


def render(lines: Sequence[PosterLine], background: Path, out: Path, style: PosterStyle) -> None:
    """Draw the post onto the background and save it to ``out``."""
    with Image.open(background) as source:
        image = source.convert("RGB")
    canvas = _Canvas(image, style)
    top = canvas.centred(style.title, style.title_top, style.title_size, WHITE) + 20
    top = canvas.centred(style.subtitle, top, style.subtitle_size, GREY) + 44

    for index, line in enumerate(_rows(lines, Tier.HEADLINE)):
        size = style.headline_sizes[min(index, len(style.headline_sizes) - 1)]
        top = canvas.banner(line.headliner or Headliner("", ""), top) + 14
        canvas.bout(line, top + size // 2, size, style.headline_margin)
        top += size + 40

    main_card = _rows(lines, Tier.MAIN_CARD)
    if main_card:
        top = canvas.section("MAIN CARD", top) + 14
        step = int(style.main_card_size * 1.3)
        for index, line in enumerate(main_card):
            canvas.bout(line, top + step * index + step // 2, style.main_card_size)
        top += step * len(main_card) + 22

    undercard = _rows(lines, Tier.UNDERCARD)
    if undercard:
        top = canvas.section("UNDERCARD", top) + 10
        spacing = (image.height - style.bottom - top) / len(undercard)
        for index, line in enumerate(undercard):
            canvas.bout(line, int(top + spacing * (index + 0.5)), style.undercard_size)
    image.save(out, quality=95)
