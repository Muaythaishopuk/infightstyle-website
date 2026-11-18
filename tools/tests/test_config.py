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
    assert config.start_time == time(13, 30)
    assert [(c.code, c.minutes) for c in config.classes] == [
        ("N", 16),
        ("C", 16),
        ("B", 19),
        ("A", 28),
    ]
    assert [(i.after_class, i.minutes) for i in config.intervals] == [("N", 15), ("C", 30)]
    assert config.sources[0].tab == "Running order"
    assert config.sources[0].billing is Billing.LISTED
    assert config.red_corner_fighters == ("Jake Newman", "Karl Ryan", "Max Manley")
