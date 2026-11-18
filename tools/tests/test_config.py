from datetime import time
from pathlib import Path

from fightcard.config import Billing, load_config

EVENTS = Path(__file__).resolve().parent.parent / "events"


def test_every_event_file_loads() -> None:
    paths = sorted(EVENTS.glob("*.json"))
    assert paths
    for path in paths:
        config = load_config(path)
        assert config.classes
        assert config.sources


def test_fight_league_one_settings() -> None:
    config = load_config(EVENTS / "2026-11-21-fight-league-1.json")
    assert config.start_time == time(13, 0)
    assert [(c.code, c.minutes) for c in config.classes] == [
        ("N", 15),
        ("C", 15),
        ("B", 20),
        ("A", 30),
    ]
    assert config.sources[1].billing is Billing.HEADLINER_FIRST
    assert config.red_corner_fighters == ("Jake Newman", "Karl Ryan")
