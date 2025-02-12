"""Test Command."""

from pytradfri.command import Command


def test_property_access() -> None:
    """Test property access in Command."""

    def error_callback(err: Exception) -> None:
        pass

    command: Command[None] = Command(
        method="method",
        path=["path"],
        data="data",
        parse_json=True,
        observe=False,
        observe_duration=0,
        err_callback=error_callback,
    )

    assert command.method == "method"
    assert command.path == ["path"]
    assert command.parse_json is True
    assert command.observe is False
    assert command.observe_duration == 0
    assert command.err_callback is error_callback


def test_result() -> None:
    """Test callback process_result."""

    def process_result(value: int) -> int:
        return value + 1

    command = Command("method", ["path"], {}, process_result=process_result)
    assert command.result is None
    assert command.raw_result is None  # type: ignore[unreachable]

    command.process_result(0)
    assert command.result == 1
    assert command.raw_result == 0


def test_url() -> None:
    """Test url is recognized."""
    command: Command[None] = Command("method", ["path"], {})
    url = command.url("host")
    assert url == "coaps://host:5684/path"

    command2: Command[None] = Command("method", ["path1", "path2"], {})
    url = command2.url("host")
    assert url == "coaps://host:5684/path1/path2"
