"""Test smart_task."""

import datetime

from pytradfri.gateway import Gateway
from pytradfri.smart_task import BitChoices, SmartTask

TASK = {
    "5850": 1,
    "9001": "Sample Name",
    "9002": 1492349682,
    "9003": 317094,
    "9040": 4,
    "9041": 48,
    "9042": {
        "15013": [
            {"5712": 18000, "5851": 254, "9003": 65537},
            {"5712": 18000, "5851": 254, "9003": 65538},
            {"5712": 19000, "5851": 230, "9003": 65539},
        ],
        "5850": 1,
    },
    "9044": [{"9046": 8, "9047": 15}],
}

TASK2 = {
    "5850": 1,
    "9002": 1492349682,
    "9003": 317094,
    "9040": 2,
    "9041": 48,
    "9042": {
        "15013": [
            {"5712": 18000, "5851": 254, "9003": 65537},
            {"5712": 18000, "5851": 254, "9003": 65538},
        ],
        "5850": 1,
    },
    "9044": [{"9046": 8, "9047": 15}],
}


TASK3 = {
    "5850": 1,
    "9002": 1492349682,
    "9003": 317094,
    "9040": 1,
    "9041": 48,
    "9042": {
        "15013": [
            {"5712": 18000, "5851": 254, "9003": 65537},
            {"5712": 18000, "5851": 254, "9003": 65538},
        ],
        "5850": 1,
    },
    "9044": [{"9046": 8, "9047": 15}],
}

TASK_OPTIONAL_DIMMER = {
    "9001": "Light and dark",
    "9002": 1613335145,
    "9003": 318615,
    "5850": 1,
    "9040": 2,
    "9041": 127,
    "9042": {"5850": 1, "15013": [{"9003": 65553}]},
    "9043": {"5850": 0, "15013": [{"9003": 65553}]},
    "9044": [{"9046": 15, "9047": 0, "9048": 7, "9049": 0, "9226": 0}],
}


WEEKDAYS = BitChoices(
    (
        ("mon", "Monday"),
        ("tue", "Tuesday"),
        ("wed", "Wednesday"),
        ("thu", "Thursday"),
        ("fri", "Friday"),
        ("sat", "Saturday"),
        ("sun", "Sunday"),
    )
)


def test_smart_task() -> None:
    """Test smart task."""
    gateway = Gateway()
    task = SmartTask(gateway, TASK)
    task1 = SmartTask(gateway, TASK2)
    task2 = SmartTask(gateway, TASK3)

    assert task.state == 1
    assert task.id == 317094
    assert task.task_type_id == 4
    assert task.repeat_days == 48
    assert task.task_start_time == datetime.time(8, 15)
    assert task.task_type_name == "Wake Up"

    assert task1.task_type_id == 2
    assert task1.task_type_name == "Lights Off"

    assert task2.task_type_id == 1
    assert task2.task_type_name == "Not At Home"


def test_smart_task_info() -> None:
    """Test gateway info."""
    gateway = Gateway()

    task = SmartTask(gateway, TASK).task_control.tasks[0]
    assert task.id == 65537
    assert task.dimmer == 254


def test_smart_task_bit_choices() -> None:
    """Test smart task with bit choices."""
    assert WEEKDAYS.get_selected_values(3) == ["Monday", "Tuesday"]


def test_smart_task_set_state() -> None:
    """Test smart task set state."""
    gateway = Gateway()
    task_control = SmartTask(gateway, TASK).task_control

    cmd = task_control.set_state(True)
    assert cmd.data == {"5850": 1, "9001": "Sample Name"}

    cmd = task_control.set_state(False)
    assert cmd.data == {"5850": 0, "9001": "Sample Name"}


def test_optional_dimmer() -> None:
    """Test a smart task with missing dimmer attribute."""
    gateway = Gateway()
    task = SmartTask(gateway, TASK_OPTIONAL_DIMMER).task_control.tasks[0]

    assert task.id == 65553
    assert task.index == 0
    assert task.state is True
    assert task.path == ["15010", "318615"]
    assert task.dimmer is None
    assert task.transition_time is None
    devices_list = task.devices_list
    assert devices_list == []
