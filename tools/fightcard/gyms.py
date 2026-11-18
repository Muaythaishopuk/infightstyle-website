"""Recognise the same gym written in different ways ("GFC", "GFC Muay Thai ")."""

from __future__ import annotations

import re

# Words that people add or leave off a gym's name without meaning a different gym.
_GENERIC_WORDS = frozenset({"muay", "thai", "mt", "gym"})
_DROPPED = re.compile("[.'\u2019]")  # "D.C.A." is "DCA", "Johnson's" is "Johnsons"
_NON_ALPHANUMERIC = re.compile(r"[^a-z0-9]+")


def gym_key(gym: str) -> str:
    """Return a comparison key for a gym name.

    Case, punctuation and generic words are ignored, so "GFC MUAY THAI", "GFC Muay Thai"
    and "GFC" share one key. A name made only of generic words keeps them, so it never
    becomes empty.
    """
    words = _NON_ALPHANUMERIC.sub(" ", _DROPPED.sub("", gym.lower())).split()
    meaningful = [word for word in words if word not in _GENERIC_WORDS]
    return " ".join(meaningful or words)
