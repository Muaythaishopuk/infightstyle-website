import argparse
import json
from pathlib import Path
from typing import Any

import pytest

from fightcard.cli import MissingSourceError, main

EVENT: dict[str, Any] = {
    "name": "Test night",
    "output_tab": "Running order",
    "start_time": "13:00",
    "classes": [{"code": "N", "label": "N Class", "minutes": 15}],
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
    assert " 1  13:00-13:15  N Class   RED Gail (GFC Muay Thai)  vs  BLUE Ann (Alpha)" in printed
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
