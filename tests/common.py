"""Provides common tools for tests."""

from pathlib import Path


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    return Path("tests/fixtures/", filename).read_text(encoding="utf8")
