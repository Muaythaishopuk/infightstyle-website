import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from tests.conftest import REAL_EVENT
from venue_layout.cli import main, write_if_changed
from venue_layout.config import EventSpec
from venue_layout.layout import build_layout
from venue_layout.svg import render_svg

SVG = "{http://www.w3.org/2000/svg}"


def test_svg_is_valid_and_draws_every_seat(event: EventSpec) -> None:
    layout = build_layout(event)
    root = ET.fromstring(render_svg(layout))  # noqa: S314 - we generated this document
    rects = root.iter(f"{SVG}rect")
    seat_fills = {tier.colour for tier in event.tiers}
    seat_rects = [r for r in rects if r.get("fill") in seat_fills and r.get("width") != "16"]
    assert len(seat_rects) == len(layout.seats)
    labels = "".join(t.text or "" for t in root.iter(f"{SVG}text"))
    for expected in (
        "RING",
        "TUNNEL",
        "FIGHTER WALKWAY",
        "30 m",
        "28 m",
        "BLEACHERS",
        "Floor chairs: 370",
        "Total with bleachers: about 570",
    ):
        assert expected in labels


def test_svg_escapes_text(event: EventSpec) -> None:
    risky = EventSpec(**{**vars(event), "title": "Fight & <Night>"})
    assert "Fight &amp; &lt;Night&gt;" in render_svg(build_layout(risky))


def test_render_is_deterministic(event: EventSpec) -> None:
    assert render_svg(build_layout(event)) == render_svg(build_layout(event))


def test_write_if_changed(tmp_path: Path) -> None:
    path = tmp_path / "sub" / "out.svg"
    assert write_if_changed(path, "a") is True
    assert write_if_changed(path, "a") is False
    assert write_if_changed(path, "b") is True
    assert path.read_text(encoding="utf-8") == "b"


def test_cli_writes_then_reports_unchanged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "plan.svg"
    assert main([str(REAL_EVENT), "--out", str(out)]) == 0
    assert "Wrote" in capsys.readouterr().out
    assert main([str(REAL_EVENT), "--out", str(out)]) == 0
    printed = capsys.readouterr().out
    assert "Unchanged" in printed
    assert "Total: 370 seats" in printed


def test_cli_default_output_sits_next_to_event(tmp_path: Path) -> None:
    event = tmp_path / "event.json"
    event.write_text(REAL_EVENT.read_text(encoding="utf-8"), encoding="utf-8")
    assert main([str(event)]) == 0
    assert (tmp_path / "layout.svg").exists()


def test_committed_plan_is_up_to_date(real_event: EventSpec) -> None:
    committed = REAL_EVENT.with_name("layout.svg").read_text(encoding="utf-8")
    assert committed == render_svg(build_layout(real_event))


def test_cli_reports_bad_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "event.json"
    bad.write_text("[]", encoding="utf-8")
    assert main([str(bad)]) == 1
    assert "error:" in capsys.readouterr().err
