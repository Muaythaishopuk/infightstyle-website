from datetime import time

import pytest

from fightcard.classes import Interval, UnknownClassError
from fightcard.schedule import build_schedule, order_by_class
from tests.builders import CLASSES, INTERVALS, bout


def test_orders_by_class_and_keeps_order_within_a_class() -> None:
    bouts = [
        bout("a1", "x", "y", "z", "A"),
        bout("n1", "x", "y", "z", "N"),
        bout("b1", "x", "y", "z", "B"),
        bout("c1", "x", "y", "z", "C"),
        bout("n2", "x", "y", "z", "N"),
    ]
    assert [b.red.name for b in order_by_class(bouts, CLASSES)] == ["n1", "n2", "c1", "b1", "a1"]


def test_unknown_class_stops_the_schedule() -> None:
    with pytest.raises(UnknownClassError):
        order_by_class([bout("k", "x", "y", "z", "K")], CLASSES)


def test_times_run_back_to_back_from_the_start() -> None:
    bouts = [
        bout("a", "x", "y", "z", "A"),
        bout("n", "x", "y", "z", "N"),
        bout("b", "x", "y", "z", "B"),
    ]
    slots = build_schedule(bouts, CLASSES, time(13, 0))
    assert [(s.number, s.start, s.finish) for s in slots] == [
        (1, time(13, 0), time(13, 15)),
        (2, time(13, 15), time(13, 35)),
        (3, time(13, 35), time(14, 5)),
    ]


def test_intervals_follow_their_class_and_are_not_numbered() -> None:
    bouts = [bout("c", "x", "y", "z", "C"), bout("n", "x", "y", "z", "N")]
    slots = build_schedule(bouts, CLASSES, time(13, 30), INTERVALS)
    assert [(s.number, s.label, s.start, s.finish) for s in slots] == [
        (1, "N Class", time(13, 30), time(13, 45)),
        (None, "Interval 1", time(13, 45), time(14, 5)),
        (2, "C Class", time(14, 5), time(14, 20)),
        (None, "Interval 2", time(14, 20), time(14, 40)),
    ]
    assert slots[1].bout is None


def test_interval_after_unknown_class_is_an_error() -> None:
    with pytest.raises(UnknownClassError):
        build_schedule([], CLASSES, time(13, 0), [Interval("K", "Break", 10)])
