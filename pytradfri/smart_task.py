"""Smart tasks set timers to turn on/off lights in various ways.

> Currently supporting wake up

SmartTask # return top level info
    TaskControl # Change top level values
    StartAction # Get top level info on start action
        StartActionItem # Get info on specific device in task
            StartActionItemController # change values for task
"""

from datetime import (datetime as dt)
import datetime

from .command import Command
from .const import (
    ATTR_ID,
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_STATE,
    ATTR_SMART_TASK_LIGHTS_OFF,
    ATTR_SMART_TASK_NOT_AT_HOME,
    ATTR_SMART_TASK_TRIGGER_TIME_INTERVAL,
    ATTR_SMART_TASK_TRIGGER_TIME_START_HOUR,
    ATTR_SMART_TASK_TRIGGER_TIME_START_MIN,
    ATTR_SMART_TASK_TYPE,
    ATTR_SMART_TASK_WAKE_UP,
    ATTR_TRANSITION_TIME,
    ATTR_REPEAT_DAYS,
    ATTR_START_ACTION,
    ROOT_START_ACTION,
    ROOT_SMART_TASKS
)
from .resource import ApiResource


class BitChoices(object):
    """Helper class for bitwise dates.

    http://stackoverflow.com/questions/3663898/representing-a-multi-select-field-for-weekdays-in-a-django-model
    """

    def __init__(self, choices):
        """Initialize BitChoices class."""
        self._choices = []
        self._lookup = {}
        for index, (key, val) in enumerate(choices):
            index = 2**index
            self._choices.append((index, val))
            self._lookup[key] = index

    def __iter__(self):
        """Iter."""
        return iter(self._choices)

    def __len__(self):
        """Len."""
        return len(self._choices)

    def __getattr__(self, attr):
        """Getattr."""
        try:
            return self._lookup[attr]
        except KeyError:
            raise AttributeError(attr)

    def get_selected_keys(self, selection):
        """Return a list of keys for the given selection."""
        return [k for k, b in self._lookup.items() if b & selection]

    def get_selected_values(self, selection):
        """Return a list of values for the given selection."""
        return [v for b, v in self._choices if b & selection]


WEEKDAYS = BitChoices(
    (
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday')
    )
)


class SmartTask(ApiResource):
    """Represent a smart task."""

    def __init__(self, gateway, raw):
        """Initialize the class."""
        super().__init__(raw)
        self._gateway = gateway

    @property
    def path(self):
        """Return gateway path."""
        return [ROOT_SMART_TASKS, self.id]

    @property
    def state(self):
        """Boolean representing the light state of the transition."""
        return self.raw.get(ATTR_LIGHT_STATE) == 1

    @property
    def task_type_id(self):
        """Return type of task."""
        return self.raw.get(ATTR_SMART_TASK_TYPE)

    @property
    def task_type_name(self):
        """Return the task type in plain text.

        (Own interpretation of names.)
        """
        if self.is_wake_up:
            return "Wake Up"
        if self.is_not_at_home:
            return "Not At Home"
        if self.if_lights_off:
            return "Lights Off"

    @property
    def is_wake_up(self):
        """Boolean representing if this is a wake up task."""
        return self.raw.get(ATTR_SMART_TASK_TYPE) == ATTR_SMART_TASK_WAKE_UP

    @property
    def is_not_at_home(self):
        """Boolean representing if this is a not home task."""
        return self.raw.get(
            ATTR_SMART_TASK_TYPE) == ATTR_SMART_TASK_NOT_AT_HOME

    @property
    def is_lights_off(self):
        """Boolean representing if this is a lights off task."""
        return self.raw.get(ATTR_SMART_TASK_TYPE) == ATTR_SMART_TASK_LIGHTS_OFF

    @property
    def repeat_days(self):
        """Return int (bit) for enabled weekdays."""
        return self.raw.get(ATTR_REPEAT_DAYS)

    @property
    def repeat_days_list(self):
        """Binary representation of weekdays the event takes place."""
        return WEEKDAYS.get_selected_values(self.raw.get(ATTR_REPEAT_DAYS))

    @property
    def task_start_parameters(self):
        """Return hour and minute that task starts."""
        return self.raw.get(ATTR_SMART_TASK_TRIGGER_TIME_INTERVAL)[0]

    @property
    def task_start_time(self):
        """Return the time the task starts.

        Time is set according to iso8601.
        """
        return datetime.time(
            self.task_start_parameters[
                ATTR_SMART_TASK_TRIGGER_TIME_START_HOUR],
            self.task_start_parameters[
                ATTR_SMART_TASK_TRIGGER_TIME_START_MIN])

    @property
    def task_control(self):
        """Method to control a task."""
        return TaskControl(
                        self,
                        self.state,
                        self.path,
                        self._gateway)

    @property
    def start_action(self):
        """Return start action object."""
        return StartAction(self, self.path)

    def __repr__(self):
        """Return a readable name for smart task."""
        state = 'on' if self.state else 'off'
        return '<Task {} - {} - {}>'.format(
            self.id, self.task_type_name, state)


class TaskControl:
    """Class to control the tasks."""

    def __init__(self, task, state, path, gateway):
        """Initialize TaskControl."""
        self._task = task
        self.state = state
        self.path = path
        self._gateway = gateway

    @property
    def tasks(self):
        """Return task objects of the task control."""
        return [StartActionItem(
            self._task,
            i,
            self.state,
            self.path,
            self.raw) for i in range(len(self.raw))]

    def set_dimmer_start_time(self, hour, minute):
        """Set start time for task (hh:mm) in iso8601.

        NB: dimmer starts 30 mins before time in app
        """
        #  This is to calculate the difference between local time
        #  and the time in the gateway
        d1 = self._gateway.get_gateway_info().current_time
        d2 = dt.utcnow()
        diff = d1 - d2
        newtime = dt(100, 1, 1, hour, minute, 00) - diff

        command = {
            ATTR_SMART_TASK_TRIGGER_TIME_INTERVAL:
                [{
                    ATTR_SMART_TASK_TRIGGER_TIME_START_HOUR: newtime.hour,
                    ATTR_SMART_TASK_TRIGGER_TIME_START_MIN: newtime.minute
                }]
            }
        return self._task.set_values(command)

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._task.raw[ATTR_START_ACTION]


class StartAction:
    """Class to control the start action-node."""

    def __init__(self, start_action, path):
        """Initialize StartAction class."""
        self.start_action = start_action
        self.path = path

    @property
    def state(self):
        """Return state of start action task."""
        return self.raw.get(ATTR_LIGHT_STATE)

    @property
    def devices(self):
        """Return state of start action task."""
        return [StartActionItem(
            self.start_action,
            i,
            self.state,
            self.path,
            self.raw) for i in range(
                len(self.raw[ROOT_START_ACTION]))]

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self.start_action.raw[ATTR_START_ACTION]


class StartActionItem:
    """Class to show settings for a task."""

    def __init__(self, task, index, state, path, raw):
        """Initialize TaskInfo."""
        self.task = task
        self.index = index
        self.state = state
        self.path = path
        self._raw = raw

    @property
    def devices_dict(self):
        """Return state of start action task."""
        json_list = {}
        z = 0
        for x in self._raw[ROOT_START_ACTION]:
            if z != self.index:
                json_list.update(x)
            z = z + 1
        return json_list

    @property
    def id(self):
        """Return ID (device id) of task."""
        return self.raw.get(ATTR_ID)

    @property
    def item_controller(self):
        """Method to control a task."""
        return StartActionItemController(
            self,
            self.raw,
            self.state,
            self.path,
            self.devices_dict)

    @property
    def transition_time(self):
        """A transition runs for this long from the time in task_start.

        Value is in seconds x 10
        """
        return self.raw.get(ATTR_TRANSITION_TIME) / 60 / 10

    @property
    def dimmer(self):
        """Return dimmer level."""
        return self.raw.get(ATTR_LIGHT_DIMMER)

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self.task.raw[ATTR_START_ACTION][ROOT_START_ACTION][self.index]

    def __repr__(self):
        """Return a readable name for this class."""
        return '<StartActionItem (Device: {} - Dimmer: {} - Time: {})>'\
            .format(self.id, self.dimmer, self.transition_time)


class StartActionItemController:
    """Class to edit settings for a task."""

    def __init__(self, item, raw, state, path, devices_dict):
        """Initialize TaskControl."""
        self._item = item
        self.raw = raw
        self.state = state
        self.path = path
        self.devices_dict = devices_dict

    def set_dimmer(self, dimmer):
        """Set final dimmer value for task."""
        command = {
            ATTR_START_ACTION: {
                    ATTR_LIGHT_STATE: self.state,
                    ROOT_START_ACTION: [{
                        ATTR_ID: self.raw[ATTR_ID],
                        ATTR_LIGHT_DIMMER: dimmer,
                        ATTR_TRANSITION_TIME: self.raw[ATTR_TRANSITION_TIME]
                    }, self.devices_dict]
                }
            }
        return self.set_values(command)

    def set_transition_time(self, transition_time):
        """Set time (mins) for light transition."""
        command = {
            ATTR_START_ACTION: {
                    ATTR_LIGHT_STATE: self.state,
                    ROOT_START_ACTION: [{
                        ATTR_ID: self.raw[ATTR_ID],
                        ATTR_LIGHT_DIMMER: self.raw[ATTR_LIGHT_DIMMER],
                        ATTR_TRANSITION_TIME: transition_time * 10 * 60
                    }, self.devices_dict]
                }
            }
        return self.set_values(command)

    def set_values(self, command):
        """
        Set values on task control.

        Returns a Command.
        """
        return Command('put', self._item.path, command)
