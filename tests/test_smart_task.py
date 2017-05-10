from pytradfri.const import (
        ROOT_SMART_TASKS
    )
from pytradfri.smart_task import SmartTask
from pytradfri.gateway import Gateway
#  from datetime import (datetime as dt)
import datetime

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


def test_smart_task(mock_api):
    mock_api.mock_request('get', [ROOT_SMART_TASKS, 271141], TASK)
    gateway = Gateway(mock_api)
    task = SmartTask(gateway, TASK)

    assert task.state == 1
    assert task.id == 317094
    assert task.task_type_id == 4
    assert task.repeat_days == 48
    assert task.task_start_time == datetime.time(8, 15)


def test_smart_task_info(mock_api):
    mock_api.mock_request('get', [ROOT_SMART_TASKS, 271141], TASK)
    gateway = Gateway(mock_api)

    task = SmartTask(gateway, TASK).task_control.tasks[0]
    assert task.id == 65537
    assert task.dimmer == 254


def test_smart_task_set_start_action_dimmer(mock_api):
    mock_api.mock_request('get', [ROOT_SMART_TASKS, 271141], TASK)
    gateway = Gateway(mock_api)

    SmartTask(gateway, TASK).start_action.devices[0].\
        item_controller.set_dimmer(30)
    assert len(mock_api.calls) == 1
    req = mock_api.calls[0]
    assert req['method'] == 'put'
