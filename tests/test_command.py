import pytest

from pytradfri.command import Command


def test_property_access():
    def pr():
        pass

    def ec():
        pass

    command = Command(
        method="method",
        path="path",
        data="data",
        parse_json=True,
        observe=False,
        observe_duration=0,
        process_result=pr,
        err_callback=ec,
    )

    assert command.method == "method"
    assert command.path == "path"
    assert command.parse_json is True
    assert command.observe is False
    assert command.observe_duration == 0
    assert command.process_result == pr
    assert command.err_callback == ec


def test_result():
    def pr(value):
        return value + 1

    command = Command("method", "path", {}, process_result=pr)
    assert command.result is None
    assert command.raw_result is None

    command.result = 0
    assert command.result == 1
    assert command.raw_result == 0


def test_url():
    command = Command("method", ["path"], {})
    url = command.url("host")
    assert url == "coaps://host:5684/path"

    command2 = Command("method", ["path1", "path2"], {})
    url = command2.url("host")
    assert url == "coaps://host:5684/path1/path2"


def test_combining_mutates():
    DATA_INT = {"key_int": 0}
    DATA_INT2 = {"key_int_2": 1}
    COMBINED_INT = {"key_int": 0, "key_int_2": 1}

    command1 = Command("method", "path", DATA_INT)
    command2 = Command("method", "path", DATA_INT2)
    combined = command1 + command2

    # Adding shouldn't mutate the original commands
    assert command1._data == DATA_INT
    assert command2._data == DATA_INT2
    assert combined._data == COMBINED_INT

    # Combining should mutate the original command
    command1.combine_data(command2)
    assert command1._data == COMBINED_INT
    assert command2._data == DATA_INT2


def test_combining_with_none():
    DATA_INT = {"key_int": 0}

    command1 = Command("method", "path", DATA_INT)
    combined = command1 + None

    assert combined._data == DATA_INT

    # Combining should mutate the original command
    command1.combine_data(None)
    assert command1._data == DATA_INT


def test_combining_integer_keys():
    DATA_INT = {"key_int": 0}
    DATA_INT_SAME_KEY = {"key_int": 1}
    DATA_INT2 = {"key_int_2": 1}
    COMBINED_INT = {"key_int": 0, "key_int_2": 1}

    command1 = Command("method", "path", DATA_INT)
    command2 = Command("method", "path", DATA_INT2)
    combined = command1 + command2
    assert combined._data == COMBINED_INT

    command1 = Command("method", "path", DATA_INT)
    command2 = Command("method", "path", DATA_INT_SAME_KEY)
    # We should always take the last key if we can't merge
    combined = command1 + command2
    assert combined._data == DATA_INT_SAME_KEY


def test_combining_string_keys():
    DATA_STRING = {"key_string": "a"}
    DATA_STRING_SAME_KEY = {"key_string": "same"}
    DATA_STRING2 = {"key_string_2": "b"}
    COMBINED_STRING = {"key_string": "a", "key_string_2": "b"}

    command1 = Command("method", "path", DATA_STRING)
    command2 = Command("method", "path", DATA_STRING2)
    combined = command1 + command2
    assert combined._data == COMBINED_STRING

    command1 = Command("method", "path", DATA_STRING)
    command2 = Command("method", "path", DATA_STRING_SAME_KEY)
    # We should always take the last key if we can't merge
    combined = command1 + command2
    assert combined._data == DATA_STRING_SAME_KEY


def test_combining_dict_keys():
    DATA_EMPTY_DICT = {"key_dict": {}}
    DATA_DICT_INT = {"key_dict": {"key_int": 0}}
    DATA_DICT_STRING = {"key_dict": {"key_string": "a"}}
    DATA_DICT_STRING2 = {"key_dict": {"key_string": "b"}}
    DATA_DICT_INTSTRING = {"key_dict": {"key_int": 0, "key_string": "a"}}

    command1 = Command("method", "path", DATA_EMPTY_DICT)
    command2 = Command("method", "path", DATA_DICT_INT)
    combined = command1 + command2
    assert combined._data == DATA_DICT_INT

    command1 = Command("method", "path", DATA_DICT_INT)
    command2 = Command("method", "path", DATA_DICT_STRING)
    combined = command1 + command2
    assert combined._data == DATA_DICT_INTSTRING

    command1 = Command("method", "path", DATA_DICT_STRING)
    command2 = Command("method", "path", DATA_DICT_STRING2)
    combined = command1 + command2
    assert combined._data == DATA_DICT_STRING2

    command1 = Command("method", "path", DATA_DICT_INT)
    command2 = Command("method", "path", DATA_DICT_STRING2)
    command3 = Command("method", "path", DATA_DICT_STRING)
    combined = command1 + command2 + command3
    assert combined._data == DATA_DICT_INTSTRING


def test_combining_list_keys():
    DATA_EMPTY_LIST = {"key_list": []}
    DATA_INT_LIST1 = {"key_list": [0, 1, 2]}
    DATA_INT_LIST2 = {"key_list": [10, 11, 12]}

    command1 = Command("method", "path", DATA_EMPTY_LIST)
    command2 = Command("method", "path", DATA_INT_LIST1)
    combined = command1 + command2
    assert combined._data == DATA_INT_LIST1

    # Duplicated keys are replaced if not dicts
    command1 = Command("method", "path", DATA_INT_LIST1)
    command2 = Command("method", "path", DATA_INT_LIST2)
    combined = command1 + command2
    assert combined._data == DATA_INT_LIST2


def test_combining_listed_dict_keys():
    DATA_EMPTY_DICT = {"key_ldict": [{}]}
    DATA_DICT_INT = {"key_ldict": [{"key_int": 0}]}
    DATA_DICT_STRING = {"key_ldict": [{"key_string": "a"}]}
    DATA_DICT_INTSTRING = {"key_ldict": [{"key_int": 0, "key_string": "a"}]}

    command1 = Command("method", "path", DATA_EMPTY_DICT)
    command2 = Command("method", "path", DATA_DICT_INT)
    combined = command1 + command2
    assert combined._data == DATA_DICT_INT

    command1 = Command("method", "path", DATA_DICT_INT)
    command2 = Command("method", "path", DATA_DICT_STRING)
    combined = command1 + command2
    assert combined._data == DATA_DICT_INTSTRING


def test_add_unsupported():
    command1 = Command("method", "path", {})
    not_a_command = 0
    with pytest.raises(TypeError):
        command1 + not_a_command
