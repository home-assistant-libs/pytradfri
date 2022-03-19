"""Test Command."""
import pytest

from pytradfri.command import Command


def test_property_access():
    """Test property access in Command."""

    def ec():
        pass

    command = Command(
        method="method",
        path="path",
        data="data",
        parse_json=True,
        observe=False,
        observe_duration=0,
        err_callback=ec,
    )

    assert command.method == "method"
    assert command.path == "path"
    assert command.parse_json is True
    assert command.observe is False
    assert command.observe_duration == 0
    assert command.err_callback == ec


def test_result():
    """Test callback process_result."""

    def pr(value):
        return value + 1

    command = Command("method", "path", {}, process_result=pr)
    assert command.result is None
    assert command.raw_result is None

    command.process_result(0)
    assert command.result == 1
    assert command.raw_result == 0


def test_url():
    """Test url is recognized."""
    command = Command("method", ["path"], {})
    url = command.url("host")
    assert url == "coaps://host:5684/path"

    command2 = Command("method", ["path1", "path2"], {})
    url = command2.url("host")
    assert url == "coaps://host:5684/path1/path2"


def test_add_unsupported():
    """Test add unsupported causes error."""
    command1 = Command("method", "path", {})
    not_a_command = 0
    with pytest.raises(TypeError):
        command1 + not_a_command
