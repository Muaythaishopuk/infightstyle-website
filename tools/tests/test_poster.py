from pathlib import Path

import pytest
from PIL import Image, ImageStat

from fightcard.poster import PosterLine, PosterStyle, fit_size, poster_lines, render
from tests.builders import bout, schedule

FONT = Path("/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf")
LABELS = ("MAIN EVENT", "CO-MAIN EVENT")


def test_lines_run_from_last_bout_to_first_with_headline_labels() -> None:
    slots = schedule(
        bout("n1", "x", "n2", "y", "N"),
        bout("cerian toland ", "x", "c2", "y", "C"),
        bout("co1", "x", "co2", "y", "A"),
        bout("main1", "x", "main2", "y", "A"),
    )
    assert poster_lines(slots, LABELS) == [
        PosterLine("MAIN1", "MAIN2", "MAIN EVENT"),
        PosterLine("CO1", "CO2", "CO-MAIN EVENT"),
        PosterLine("CERIAN TOLAND", "C2", None),
        PosterLine("N1", "N2", None),
    ]


def test_fit_size_shrinks_until_text_fits() -> None:
    assert fit_size(lambda size: size * 10, max_width=500, size=80) == 50
    assert fit_size(lambda size: size * 10, max_width=5000, size=80) == 80
    assert fit_size(lambda _: 10**9, max_width=1, size=5) == 1


@pytest.mark.skipif(not FONT.exists(), reason="poster font not installed")
def test_render_keeps_the_background_size_and_draws_on_it(tmp_path: Path) -> None:
    background = tmp_path / "bg.png"
    Image.new("RGB", (400, 500), (0, 0, 0)).save(background)
    out = tmp_path / "post.jpg"
    style = PosterStyle(font=FONT, title="RUNNING ORDER", subtitle="TEST", margin=20, title_top=20)
    lines = [PosterLine("A VERY LONG NAME INDEED", "B", "MAIN EVENT"), PosterLine("C", "D", None)]
    render(lines, background, out, style)
    with Image.open(out) as image:
        assert image.size == (400, 500)
        assert ImageStat.Stat(image.convert("L")).extrema[0][1] > 200
