import datetime

from pytradfri.gateway import Gateway
from pytradfri.smart_task import BitChoices, SmartTask

TASK = {
    "5850": 1,
    "9002": 1492349682,
    "9003": 317094,
    "9040": 4,
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


def test_smart_task():
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


def test_smart_task_info():
    gateway = Gateway()

    task = SmartTask(gateway, TASK).task_control.tasks[0]
    assert task.id == 65537
    assert task.dimmer == 254


def test_smart_task_set_start_action_dimmer():
    gateway = Gateway()

    cmd = (
        SmartTask(gateway, TASK).start_action.devices[0].item_controller.set_dimmer(30)
    )

    assert cmd.method == "put"
    assert cmd.path == ["15010", 317094]
    assert cmd.data == {
        "9042": {
            "15013": [
                {"5712": 18000, "5851": 30, "9003": 65537},
                {"5712": 18000, "5851": 254, "9003": 65538},
            ],
            "5850": 1,
        }
    }


def test_smart_task_bit_choices():
    assert WEEKDAYS.get_selected_values(3) == ["Monday", "Tuesday"]
