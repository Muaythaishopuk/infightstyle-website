import pytest

from venue_layout.geometry import Rect, whole_fits


def test_edges_and_centre() -> None:
    area = Rect(1, 2, 4, 6)
    assert (area.right, area.bottom, area.centre) == (5, 8, (3, 5))


def test_centred() -> None:
    assert Rect.centred(10, 10, 4, 2) == Rect(8, 9, 4, 2)


def test_negative_size_rejected() -> None:
    with pytest.raises(ValueError, match="negative"):
        Rect(0, 0, -1, 1)


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        (Rect(1, 1, 2, 2), True),
        (Rect(2, 0, 2, 2), False),  # shares an edge only
        (Rect(5, 5, 1, 1), False),
    ],
)
def test_overlaps(other: Rect, *, expected: bool) -> None:
    assert Rect(0, 0, 2, 2).overlaps(other) is expected
    assert other.overlaps(Rect(0, 0, 2, 2)) is expected


def test_contains() -> None:
    outer = Rect(0, 0, 10, 10)
    assert outer.contains(Rect(0, 0, 10, 10))
    assert not outer.contains(Rect(9, 9, 2, 1))


def test_inset_and_grow() -> None:
    assert Rect(0, 0, 10, 6).inset(1) == Rect(1, 1, 8, 4)
    assert Rect(0, 0, 2, 2).inset(5) == Rect(5, 5, 0, 0)
    assert Rect(0, 2, 4, 1).grow_vertically(0.5) == Rect(0, 1.5, 4, 2)


def test_whole_fits() -> None:
    assert whole_fits(3.0, 0.75) == 4  # exact fit despite floating point
    assert whole_fits(1.0, 0.3) == 3
    assert whole_fits(-1.0, 0.5) == 0
