from pytradfri.smart_task import SmartTask

TASK = {
    '5850': 1,
    '9002': 1492349682,
    '9003': 317094,
    '9040': 4,
    '9041': 48,
    '9042': {
                '15013':
                [
                    {'5712': 18000, '5851': 254, '9003': 65537},
                    {'5712': 18000, '5851': 254, '9003': 65538}
                ],
                '5850': 1},
    '9044': [
                {'9046': 8, '9047': 15}
            ]
        }


def test_smart_task():
    task = SmartTask(None, TASK)

    assert task.state == 1
    assert task.id == 317094
    assert task.task_type_id == 4
    assert task.repeat_days == 48
    assert task.task_start_time_seconds == 29700


def test_smart_task_info():
    task = SmartTask(None, TASK).task_control.tasks[0]
    assert task.id == 65537
    assert task.dimmer == 254
