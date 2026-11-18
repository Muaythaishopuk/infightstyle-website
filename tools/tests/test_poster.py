from pathlib import Path

import pytest
from PIL import Image, ImageStat

from fightcard.poster import (
    Headliner,
    PosterLine,
    PosterStyle,
    Tier,
    fit_size,
    poster_lines,
    render,
)
from tests.builders import bout, schedule

FONT = Path("/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf")
HEADLINERS = (Headliner("MAIN EVENT", "WORLD TITLE"), Headliner("CO-MAIN EVENT", "EURO TITLE"))


def test_lines_run_from_last_bout_to_first_in_three_tiers() -> None:
    slots = schedule(
        bout("n1", "x", "n2", "y", "N"),
        bout("cerian toland ", "x", "c2", "y", "C"),
        bout("b1", "x", "b2", "y", "B"),
        bout("co1", "x", "co2", "y", "A"),
        bout("main1", "x", "main2", "y", "A"),
    )
    assert poster_lines(slots, HEADLINERS, {"A", "B"}) == [
        PosterLine("MAIN1", "MAIN2", Tier.HEADLINE, HEADLINERS[0]),
        PosterLine("CO1", "CO2", Tier.HEADLINE, HEADLINERS[1]),
        PosterLine("B1", "B2", Tier.MAIN_CARD),
        PosterLine("CERIAN TOLAND", "C2", Tier.UNDERCARD),
        PosterLine("N1", "N2", Tier.UNDERCARD),
    ]


def test_fit_size_shrinks_until_text_fits() -> None:
    assert fit_size(lambda size: size * 10, max_width=500, size=80) == 50
    assert fit_size(lambda size: size * 10, max_width=5000, size=80) == 80
    assert fit_size(lambda _: 10**9, max_width=1, size=5) == 1


def _render(tmp_path: Path, lines: list[PosterLine]) -> Image.Image:
    background = tmp_path / "bg.png"
    Image.new("RGB", (800, 1000), (0, 0, 0)).save(background)
    out = tmp_path / "post.jpg"
    style = PosterStyle(font=FONT, title="RUNNING ORDER", subtitle="TEST", title_top=20)
    render(lines, background, out, style)
    return Image.open(out)


FULL_CARD = [
    PosterLine("A VERY LONG NAME INDEED", "B", Tier.HEADLINE, HEADLINERS[0]),
    PosterLine("C", "D", Tier.HEADLINE, HEADLINERS[1]),
    PosterLine("C", "D", Tier.HEADLINE, HEADLINERS[1]),
    PosterLine("E", "F", Tier.MAIN_CARD),
    PosterLine("G", "H", Tier.UNDERCARD),
]


@pytest.mark.skipif(not FONT.exists(), reason="poster font not installed")
@pytest.mark.parametrize("lines", [FULL_CARD, FULL_CARD[:1]], ids=["every tier", "headline only"])
def test_render_draws_on_a_background_sized_post(tmp_path: Path, lines: list[PosterLine]) -> None:
    with _render(tmp_path, lines) as image:
        assert image.size == (800, 1000)
        assert ImageStat.Stat(image.convert("L")).extrema[0][1] > 200
