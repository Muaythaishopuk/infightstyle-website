import argparse
import json
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from fightcard.cli import MissingSourceError, PosterSettingsError, main

EVENT: dict[str, Any] = {
    "name": "Test night",
    "output_tab": "Running order",
    "start_time": "13:00",
    "classes": [{"code": "N", "label": "N Class", "minutes": 15}],
    "intervals": [{"after_class": "N", "label": "Break", "minutes": 10}],
    "sources": [
        {
            "tab": "Card ",
            "billing": "listed",
            "header_rows": 1,
            "columns": {
                "fight_class": 0,
                "red_name": 1,
                "red_gym": 2,
                "blue_name": 3,
                "blue_gym": 4,
            },
        }
    ],
    "red_corner_gyms": ["GFC"],
}


def _write(path: Path, data: object) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _weigh_in_event(tmp_path: Path, sources: object, overrides: dict[str, int]) -> Path:
    weigh_in = {
        "output_tab": "Weigh in",
        "default_allowance_kg": 0.5,
        "allowance_overrides_kg": overrides,
        "weight_sources": sources,
    }
    return _write(tmp_path / "weigh.json", {**EVENT, "weigh_in": weigh_in})


def _run(tmp_path: Path, *extra: str) -> dict[str, Any]:
    event = _write(tmp_path / "event.json", EVENT)
    rows = [
        ["Class"],
        ["N Class", "Ann", "Alpha", "Gail", "GFC Muay Thai"],
        ["N Class", "", "DCA", "Hal", "Hotel"],
    ]
    card = _write(tmp_path / "card.json", {"range": "Card!A1", "values": rows})
    out = tmp_path / "payload.json"
    assert main([str(event), "--source", f"Card ={card}", "--out", str(out), *extra]) == 0
    payload: dict[str, Any] = json.loads(out.read_text(encoding="utf-8"))
    return payload


def test_writes_payload_with_swapped_corners_and_warnings(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = _run(tmp_path)
    assert payload["range"] == "'Running order'!A1"
    assert payload["values"][1][4:8] == ["'Gail", "'GFC Muay Thai", "'Ann", "'Alpha"]
    assert payload["warnings"] == ["Card row 3: fighter from DCA is TBC."]
    assert "requests" not in payload
    printed = capsys.readouterr().out
    assert " 1  13:00-13:15  N Class     RED Gail (GFC Muay Thai)  vs  BLUE Ann (Alpha)" in printed
    assert "    13:30-13:40  Break" in printed
    assert "WARNING: Card row 3" in printed


def test_sheet_id_adds_formatting_requests(tmp_path: Path) -> None:
    payload = _run(tmp_path, "--sheet-id", "7")
    assert payload["requests"][0]["repeatCell"]["range"]["sheetId"] == 7


def test_missing_source_tab_is_an_error(tmp_path: Path) -> None:
    event = _write(tmp_path / "event.json", EVENT)
    with pytest.raises(MissingSourceError, match="'Card '"):
        main([str(event), "--out", str(tmp_path / "out.json")])


def test_badly_formed_source_is_an_error(tmp_path: Path) -> None:
    event = _write(tmp_path / "event.json", EVENT)
    with pytest.raises(argparse.ArgumentTypeError, match=r"TAB=path\.json"):
        main([str(event), "--source", "no-equals-sign", "--out", str(tmp_path / "o.json")])


def test_empty_source_tab_gives_no_bouts(tmp_path: Path) -> None:
    event = _write(tmp_path / "event.json", EVENT)
    card = _write(tmp_path / "card.json", {"range": "Card!A1"})
    out = tmp_path / "o.json"
    main([str(event), "--source", f"Card ={card}", "--out", str(out)])
    assert json.loads(out.read_text(encoding="utf-8"))["values"][0][0] == "Bout"


def test_rebuilding_from_its_own_output_changes_nothing(tmp_path: Path) -> None:
    first = _run(tmp_path)
    displayed = [[str(c).removeprefix("'") for c in row] for row in first["values"]]
    columns = {"fight_class": 3, "red_name": 4, "red_gym": 5, "blue_name": 6, "blue_gym": 7}
    source = {"tab": "Running order", "billing": "listed", "header_rows": 1, "columns": columns}
    event = _write(tmp_path / "rebuild.json", {**EVENT, "sources": [source]})
    tab = _write(tmp_path / "tab.json", {"values": displayed})
    out = tmp_path / "second.json"
    main([str(event), "--source", f"Running order={tab}", "--out", str(out)])
    assert json.loads(out.read_text(encoding="utf-8"))["values"] == first["values"]


def test_weigh_in_tab_is_built_from_the_weight_tab(tmp_path: Path) -> None:
    columns = {**EVENT["sources"][0]["columns"], "red_weight": 5, "blue_weight": 6}
    weights = {"tab": "Weights", "billing": "listed", "header_rows": 1, "columns": columns}
    event = _weigh_in_event(tmp_path, [weights], {"Gail": 0})
    rows = [["Class"], ["N Class", "Ann", "Alpha", "Gail", "GFC", "60kg", "61kg"]]
    card = _write(tmp_path / "card.json", {"values": rows[:2]})
    weight_tab = _write(tmp_path / "weights.json", {"values": rows})
    out = tmp_path / "out.json"
    args = [str(event), "--source", f"Card ={card}", "--source", f"Weights={weight_tab}"]
    main([*args, "--out", str(out), "--weigh-in-sheet-id", "9"])
    payload = json.loads(out.read_text(encoding="utf-8"))["weigh_in"]
    assert payload["range"] == "'Weigh in'!A1"
    assert [row[:6] for row in payload["values"][1:]] == [
        [1, "Red", "'Gail", "'GFC", 61.0, 0.0],
        [1, "Blue", "'Ann", "'Alpha", 60.0, 0.5],
    ]
    assert payload["requests"][0]["repeatCell"]["range"]["sheetId"] == 9


def test_weigh_in_without_sheet_id_has_no_formatting(tmp_path: Path) -> None:
    event = _weigh_in_event(tmp_path, EVENT["sources"], {})
    card = _write(tmp_path / "card.json", {"values": [["Class"], ["N Class", "A", "B", "C", "D"]]})
    out = tmp_path / "out.json"
    main([str(event), "--source", f"Card ={card}", "--out", str(out)])
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "requests" not in payload["weigh_in"]
    assert "No weight for C in bout 1." in payload["warnings"]


def test_poster_needs_its_settings(tmp_path: Path) -> None:
    event = _write(tmp_path / "event.json", EVENT)
    card = _write(tmp_path / "card.json", {"values": [["Class"]]})
    with pytest.raises(PosterSettingsError, match="poster"):
        main(
            [
                str(event),
                "--source",
                f"Card ={card}",
                "--out",
                str(tmp_path / "o.json"),
                "--poster-out",
                str(tmp_path / "p.jpg"),
            ]
        )


def test_poster_is_saved(tmp_path: Path) -> None:
    font = "/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf"
    if not Path(font).exists():
        pytest.skip("poster font not installed")
    poster = {"title": "RUNNING ORDER", "subtitle": "TEST", "font": font}
    event = _write(tmp_path / "event.json", {**EVENT, "poster": poster})
    card = _write(tmp_path / "card.json", {"values": [["Class"], ["N Class", "A", "B", "C", "D"]]})
    background = tmp_path / "bg.png"
    Image.new("RGB", (800, 1000)).save(background)
    out = tmp_path / "p.jpg"
    args = [str(event), "--source", f"Card ={card}", "--out", str(tmp_path / "o.json")]
    main([*args, "--poster-background", str(background), "--poster-out", str(out)])
    assert out.exists()
