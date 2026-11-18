import pytest

from fightcard.classes import UnknownClassError, class_by_code, parse_class_code
from tests.builders import CLASSES


@pytest.mark.parametrize(
    ("text", "code"),
    [
        ("N Class", "N"),
        (" n class ", "N"),
        ("C class pro ", "C"),
        ("C Class Pro-Am", "C"),
        (" A CLASS ", "A"),
        ("B CLASS ", "B"),
    ],
)
def test_reads_class_letter(text: str, code: str) -> None:
    assert parse_class_code(text) == code


@pytest.mark.parametrize("text", ["", "£4,600", "Class", "vs", "NClass"])
def test_text_without_a_class_gives_none(text: str) -> None:
    assert parse_class_code(text) is None


def test_finds_class_by_code() -> None:
    assert class_by_code(CLASSES, "B").minutes == 20


def test_unknown_class_is_an_error() -> None:
    with pytest.raises(UnknownClassError, match="'K'"):
        class_by_code(CLASSES, "K")
