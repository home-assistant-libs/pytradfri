"""Smart tasks set timers to turn on/off lights in various ways.

> Currently supporting wake up

SmartTask # return top level info
    TaskControl # Change top level values
    StartAction # Get top level info on start action
        StartActionItem # Get info on specific device in task
            StartActionItemController # change values for task
"""
from __future__ import annotations

from datetime import datetime as dt, time, timedelta
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, Field

from .command import Command
from .const import (
    ATTR_DEVICE_STATE,
    ATTR_GATEWAY_INFO,
    ATTR_ID,
    ATTR_LIGHT_DIMMER,
    ATTR_NAME,
    ATTR_REPEAT_DAYS,
    ATTR_SMART_TASK_LIGHTS_OFF,
    ATTR_SMART_TASK_NOT_AT_HOME,
    ATTR_SMART_TASK_TRIGGER_TIME_INTERVAL,
    ATTR_SMART_TASK_TRIGGER_TIME_START_HOUR,
    ATTR_SMART_TASK_TRIGGER_TIME_START_MIN,
    ATTR_SMART_TASK_TYPE,
    ATTR_SMART_TASK_WAKE_UP,
    ATTR_START_ACTION,
    ATTR_TIME_START_TIME_MINUTE,
    ATTR_TRANSITION_TIME,
    ROOT_GATEWAY,
    ROOT_SMART_TASKS,
    ROOT_START_ACTION,
)
from .resource import ApiResource, ApiResourceResponse, BaseResponse, TypeRaw
from .util import BitChoices

if TYPE_CHECKING:
    from .gateway import Gateway, GatewayInfo


WEEKDAYS: BitChoices = BitChoices(
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


class SmartTaskMixin(BaseModel):
    """Represent common task attributes."""

    state: int = Field(alias=ATTR_DEVICE_STATE)


class StartActionResponse(BaseResponse):
    """Represent a start action response."""

    transition_time: Optional[int] = Field(alias=ATTR_TRANSITION_TIME)
    dimmer: Optional[int] = Field(alias=ATTR_LIGHT_DIMMER)


class TimeIntervalResponse(BaseModel):
    """Represent a time interval response."""

    hour_start: int = Field(alias=ATTR_SMART_TASK_TRIGGER_TIME_START_HOUR)
    minute_start: int = Field(alias=ATTR_TIME_START_TIME_MINUTE)


class RootStartActionResponse(SmartTaskMixin, BaseModel):
    """Represent a smart action response."""

    root_start_action: list[StartActionResponse] = Field(
        alias=ROOT_START_ACTION, default=[]
    )


class SmartTaskResponse(SmartTaskMixin, ApiResourceResponse):
    """Represent a smart task response."""

    smart_task_type: int = Field(alias=ATTR_SMART_TASK_TYPE)
    repeat_days: int = Field(alias=ATTR_REPEAT_DAYS)
    start_action: RootStartActionResponse = Field(alias=ATTR_START_ACTION)
    time_interval: list[TimeIntervalResponse] = Field(
        alias=ATTR_SMART_TASK_TRIGGER_TIME_INTERVAL
    )


class SmartTask(ApiResource):
    """Represent a smart task."""

    _model_class: type[SmartTaskResponse] = SmartTaskResponse
    raw: SmartTaskResponse

    def __init__(self, gateway: Gateway, raw: TypeRaw) -> None:
        """Initialize the class."""
        super().__init__(raw)
        self._gateway = gateway
        self.delta_time_gateway_local = timedelta(0)

    @property
    def path(self) -> list[str]:
        """Return gateway path."""
        return [ROOT_SMART_TASKS, str(self.id)]

    @property
    def state(self) -> bool:
        """Boolean representing the light state of the transition."""
        return self.raw.state == 1

    @property
    def task_type_id(self) -> int:
        """Return type of task."""
        return self.raw.smart_task_type

    @property
    def task_type_name(self) -> str | None:
        """Return the task type in plain text.

        (Own interpretation of names.)
        """
        if self.is_wake_up:
            return "Wake Up"
        if self.is_not_at_home:
            return "Not At Home"
        if self.is_lights_off:
            return "Lights Off"
        return None

    @property
    def is_wake_up(self) -> bool:
        """Boolean representing if this is a wake up task."""
        return self.raw.smart_task_type == ATTR_SMART_TASK_WAKE_UP

    @property
    def is_not_at_home(self) -> bool:
        """Boolean representing if this is a not home task."""
        return self.raw.smart_task_type == ATTR_SMART_TASK_NOT_AT_HOME

    @property
    def is_lights_off(self) -> bool:
        """Boolean representing if this is a lights off task."""
        return self.raw.smart_task_type == ATTR_SMART_TASK_LIGHTS_OFF

    @property
    def repeat_days(self) -> int:
        """Return int (bit) for enabled weekdays."""
        return self.raw.repeat_days

    @property
    def repeat_days_list(self) -> list[str]:
        """Binary representation of weekdays the event takes place."""
        return WEEKDAYS.get_selected_values(self.repeat_days)

    @property
    def task_start_parameters(self) -> TimeIntervalResponse:
        """Return hour and minute that task starts."""
        return self.raw.time_interval[0]

    @property
    def task_start_time(self) -> time:
        """Return the time the task starts.

        Time is set according to iso8601.
        """
        return time(
            self.task_start_parameters.hour_start,
            self.task_start_parameters.minute_start,
        )

    @property
    def task_control(self) -> TaskControl:
        """Control a task."""
        return TaskControl(self, self.state, self.path, self._gateway)

    @property
    def start_action(self) -> StartAction:
        """Return start action object."""
        return StartAction(self, self.path)

    def __repr__(self) -> str:
        """Return a readable name for smart task."""
        state = "on" if self.state else "off"
        return f"<Task {self.id} - {self.task_type_name} - {state}>"


class TaskControl:
    """Class to control the tasks."""

    def __init__(
        self, task: SmartTask, state: bool, path: list[str], gateway: Gateway
    ) -> None:
        """Initialize TaskControl."""
        self._task = task
        self.state = state
        self.path = path
        self._gateway = gateway

    @property
    def tasks(self) -> list[StartActionItem]:
        """Return task objects of the task control."""
        return [
            StartActionItem(self._task, idx, self.state, self.path, self.raw)
            for idx in range(len(self.raw.root_start_action))
        ]

    def calibrate_time(self) -> Command[None]:
        """Calibrate difference between local time and gateway time."""

        def process_result(result: TypeRaw) -> None:
            gateway_info: GatewayInfo = GatewayInfo(result)
            if not gateway_info.current_time:
                return

            d_now = gateway_info.current_time
            d_utcnow = dt.utcnow()
            diff = d_now - d_utcnow

            self._task.delta_time_gateway_local = diff

        return Command(
            "get", [ROOT_GATEWAY, ATTR_GATEWAY_INFO], process_result=process_result
        )

    def set_dimmer_start_time(self, hour: int, minute: int) -> Command[None]:
        """Set start time for task (hh:mm) in iso8601.

        NB: dimmer starts 30 mins before time in app
        """
        new_time: dt = (
            dt(100, 1, 1, hour, minute, 00) - self._task.delta_time_gateway_local
        )

        command: dict[str, list[dict[str, int]]] = {
            ATTR_SMART_TASK_TRIGGER_TIME_INTERVAL: [
                {
                    ATTR_SMART_TASK_TRIGGER_TIME_START_HOUR: new_time.hour,
                    ATTR_SMART_TASK_TRIGGER_TIME_START_MIN: new_time.minute,
                }
            ]
        }
        return self._task.set_values(command)

    def set_state(self, state: bool) -> Command[None]:
        """Set state of a task."""
        return self._task.set_values(
            {ATTR_DEVICE_STATE: int(state), ATTR_NAME: self._task.name}
        )

    @property
    def raw(self) -> RootStartActionResponse:
        """Return raw data that it represents."""
        return self._task.raw.start_action


class StartAction:
    """Class to control the start action-node."""

    def __init__(self, smart_task: SmartTask, path: list[str]) -> None:
        """Initialize StartAction class."""
        self.smart_task = smart_task
        self.path = path

    @property
    def state(self) -> bool:
        """Return state of start action task."""
        return self.raw.state == 1

    @property
    def raw(self) -> RootStartActionResponse:
        """Return raw data that it represents."""
        return self.smart_task.raw.start_action


class StartActionItem:
    """Class to show settings for a task."""

    def __init__(
        self,
        task: SmartTask,
        index: int,
        state: bool,
        path: list[str],
        raw: RootStartActionResponse,
    ):
        """Initialize TaskInfo."""
        self.task = task
        self.index = index
        self.state = state
        self.path = path
        self._raw = raw

    @property
    def devices_list(self) -> list[dict[str, int]]:
        """Store task data for all tasks but the one we want to update."""
        output_list: list[dict[str, int]] = []
        current_data_list: list[StartActionResponse] = self._raw.root_start_action
        for idx, record in enumerate(current_data_list):
            if idx != self.index:
                list_record: dict[str, int] = {}
                list_record[ATTR_ID] = record.id
                if record.dimmer is not None:
                    list_record[ATTR_LIGHT_DIMMER] = record.dimmer

                if record.transition_time is not None:
                    list_record[ATTR_TRANSITION_TIME] = record.transition_time

                output_list.append(list_record)

        return output_list

    @property
    def id(self) -> int:
        """Return ID (device id) of task."""
        return self.raw.id

    @property
    def item_controller(self) -> StartActionItemController:
        """Control a task."""
        return StartActionItemController(
            self, self.raw, self.state, self.path, self.devices_list
        )

    @property
    def transition_time(self) -> int | None:
        """Transition runs for this long from the time in task_start.

        Value is in seconds x 10. Default to 0 if transition is missing.
        """
        if self.raw.transition_time is not None:
            return round(self.raw.transition_time / 60 / 10)

        return None

    @property
    def dimmer(self) -> int | None:
        """Return dimmer level."""
        return self.raw.dimmer

    @property
    def raw(self) -> StartActionResponse:
        """Return raw data that it represents."""
        return self._raw.root_start_action[self.index]

    def __repr__(self) -> str:
        """Return a readable name for this class."""
        return (
            f"<StartActionItem (Device: {self.id} - Dimmer: {self.dimmer} - "
            f"Time: {self.transition_time})>"
        )


class StartActionItemController:
    """Class to edit settings for a task."""

    def __init__(
        self,
        item: StartActionItem,
        raw: StartActionResponse,
        state: bool,
        path: list[str],
        devices_list: list[dict[str, int]],
    ):
        """Initialize StartActionItemController."""
        self._item = item
        self.raw = raw
        self.state = state
        self.path = path
        self.devices_list = devices_list

    def set_dimmer(self, dimmer: int) -> Command[None]:
        """Set final dimmer value for task."""
        root_start_action_list: list[dict[str, int]] = [
            {
                ATTR_ID: self.raw.id,
                ATTR_LIGHT_DIMMER: dimmer,
            }
        ]

        if self.raw.transition_time is not None:
            root_start_action_list[0][ATTR_TRANSITION_TIME] = self.raw.transition_time

        root_start_action_list.extend(self.devices_list)

        command: dict[str, dict[str, Any]] = {
            ATTR_START_ACTION: {
                ATTR_DEVICE_STATE: int(self.state),
                ROOT_START_ACTION: root_start_action_list,
            }
        }
        return self.set_values(command)

    def set_transition_time(self, transition_time: int) -> Command[None]:
        """Set time (mins) for light transition."""
        root_start_action_list: list[dict[str, int]] = [
            {
                ATTR_ID: self.raw.id,
                ATTR_TRANSITION_TIME: transition_time * 10 * 60,
            }
        ]

        if self.raw.dimmer is not None:
            root_start_action_list[0][ATTR_LIGHT_DIMMER] = self.raw.dimmer

        root_start_action_list.extend(self.devices_list)

        command: dict[str, dict[str, Any]] = {
            ATTR_START_ACTION: {
                ATTR_DEVICE_STATE: int(self.state),
                ROOT_START_ACTION: root_start_action_list,
            }
        }
        return self.set_values(command)

    def set_values(self, values: dict[str, dict[str, Any]]) -> Command[None]:
        """
        Set values on task control.

        Returns a Command.
        """
        return Command("put", self._item.path, values)
