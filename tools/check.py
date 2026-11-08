"""Run every quality gate: formatting, linting, types, tests and copy-paste detection.

Usage (from the ``tools`` folder): ``python check.py``. Exits non-zero if any gate fails.
"""

from __future__ import annotations

import subprocess
import sys

GATES: tuple[tuple[str, list[str]], ...] = (
    ("format", [sys.executable, "-m", "ruff", "format", "--check", "."]),
    ("lint", [sys.executable, "-m", "ruff", "check", "."]),
    ("types", [sys.executable, "-m", "mypy"]),
    ("tests", [sys.executable, "-m", "pytest", "-q"]),
    ("duplication", ["npx", "--yes", "jscpd@4", "--config", ".jscpd.json"]),
)


def main() -> int:
    """Run each gate in turn and report which ones failed."""
    failed = [
        name
        for name, command in GATES
        if subprocess.run(command, check=False).returncode != 0  # noqa: S603
    ]
    if failed:
        sys.stderr.write(f"FAILED: {', '.join(failed)}\n")
        return 1
    sys.stdout.write("All checks passed.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
