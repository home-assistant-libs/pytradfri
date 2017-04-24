"""Smart tasks set timers to turn on/off lights in various ways.

v1: Added support to show (not modify) states for wake up smart task.

To-do:
> Represent start_action as a class
> Refactor start_action_state as a method

"""

from datetime import datetime
from .const import (
    ATTR_CREATED_AT,
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
        return iter(self._choices)

    def __len__(self):
        return len(self._choices)

    def __getattr__(self, attr):
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


class SmartTask(object):
    """Represent a group."""

    def __init__(self, api, raw):
        """Initialize smart task class."""
        self.api = api
        self.raw = raw

    @property
    def path(self):
        """Return gateway path."""
        return [ROOT_SMART_TASKS, self.id]

    @property
    def state(self):
        """Boolean representing the light state of the transition."""
        return self.raw.get(ATTR_LIGHT_STATE) == 1

    @property
    def created_at(self):
        """Return when task was created."""
        if ATTR_CREATED_AT not in self.raw:
            return None
        return datetime.utcfromtimestamp(self.raw[ATTR_CREATED_AT])

    @property
    def id(self):
        """Return ID# of task."""
        return self.raw.get(ATTR_ID)

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
    def start_action(self):
        """Return state and all devices in smart action."""
        return self.raw.get(ATTR_START_ACTION)

    @property
    def start_action_state(self):
        """Return state of start action task."""
        return self.start_action[ATTR_LIGHT_STATE]

    @property
    def task_start_parameters(self):
        """Return hour and minute that task starts."""
        return self.raw.get(ATTR_SMART_TASK_TRIGGER_TIME_INTERVAL)[0]

    @property
    def task_start_time_seconds(self):
        """Return the hour and minute (represented in seconds) the task starts.

        Time is set according to iso8601.
        """
        hour = self.task_start_parameters[
            ATTR_SMART_TASK_TRIGGER_TIME_START_HOUR] * 60 * 60
        min = self.task_start_parameters[
            ATTR_SMART_TASK_TRIGGER_TIME_START_MIN] * 60

        return hour + min

    @property
    def task_control(self):
        """Method to control a task."""
        return TaskControl(self)

    def __repr__(self):
        """Return a readable name for smart task."""
        state = 'on' if self.state else 'off'
        return '<Task {} - {} - {}>'.format(
            self.id, self.task_type_name, state)

    def update(self):
        """Update the group."""
        self.raw = self.api('get', self.path)


class TaskControl:
    """Class to control the tasks."""

    def __init__(self, task):
        """Initialize TaskControl."""
        self._task = task

    @property
    def tasks(self):
        """Return task objects of the task control."""
        return [TaskInfo(self._task, i) for i in range(len(self.raw))]

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._task.raw[ATTR_START_ACTION][ROOT_START_ACTION]


class TaskInfo:
    """Class to show settings for a task."""

    def __init__(self, task, index):
        """Initialize TaskInfo."""
        self.task = task
        self.index = index

    @property
    def id(self):
        """Return ID (device id) of task."""
        return self.raw.get(ATTR_ID)

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
