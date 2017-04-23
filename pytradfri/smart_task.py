"""Smart tasks set timers to turn on/off lights in various ways.

v1:

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


# The gateway stores days as bit
CONST_ONCE = 0
CONST_MON = 1
CONST_TUE = 2
CONST_WED = 4
CONST_THU = 8
CONST_FRI = 16
CONST_SAT = 32
CONST_SUN = 64


class SmartTask:
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
        """Numeric (binary) representation of weekdays the event takes place."""
        return self.raw.get(ATTR_REPEAT_DAYS)

    @property
    def repeat_days_bin(self):
        """Binary representation of weekdays the event takes place."""
        return bin(self.raw.get(ATTR_REPEAT_DAYS))

    @property
    def start_action(self):
        return self.raw.get(ATTR_START_ACTION)

    @property
    def start_action_state(self):
        return self.start_action[ATTR_LIGHT_STATE]

    @property
    def task_start_parameters(self):
        return self.raw.get(ATTR_SMART_TASK_TRIGGER_TIME_INTERVAL)[0]

    @property
    def task_start_time_seconds(self):
        """Return the hour and minute (represented in seconds) the task starts.

        Time is set according to iso8601
        """
        hour = self.task_start_parameters[
            ATTR_SMART_TASK_TRIGGER_TIME_START_HOUR] * 60 * 60
        min = self.task_start_parameters[
            ATTR_SMART_TASK_TRIGGER_TIME_START_MIN] * 60

        return hour + min

    @property
    def task_control(self):
        return TaskControl(self)

    def __repr__(self):
        state = 'on' if self.state else 'off'
        return '<Task {} - {} - {}>'.format(
            self.id, self.task_type_name, state)

    def update(self):
        """Update the group."""
        self.raw = self.api('get', self.path)

#  >>> light.light_control.lights[0].dimmer
#  >>> task.light_control.tasks
#  '9042': {'15013': [{'5712': 18000, '5851': 254, '9003': 65538},
#                     {'5712': 18000, '5851': 254, '9003': 65537}],
#           '5850': 1},


class TaskControl:
    """Class to control the tasks."""

    def __init__(self, task):
        """Initialize TaskControl."""
        self._task = task

    @property
    def tasks(self):
        """Return task objects of the task control."""
        return [TaskInfo(self._task, i) for i in range(len(self.raw))]

    def set_dimmer(self, dimmer, *, index=0):
        """Set dimmer value of a light.

        Integer between 0..255
        """
        self.set_values({
            ATTR_LIGHT_DIMMER: dimmer,
        }, index=index)

    @property
    def create_commando(self):
        nested = {'babba', 'goo'}
        data = {
           ATTR_START_ACTION: 'ACME',
           'shares': 100,
           'price': nested
        }
        json_str = json.dumps(data)
        return json_str

    def set_transiton_time(self, transition_time, *, index=0):
        """Set transition time for dimmer."""
        self.set_values({
            ATTR_TRANSITION_TIME: transition_time * 60 * 10,
        }, index=index)

    def set_values(self, values, *, index=0):
        """Set values on light control."""
#        assert len(self.raw) == 1, \
#            'Only devices with 1 light supported'
        print(self._task.path)
        print(values)
        jsonstring = ATTR_START_ACTION
        print(jsonstring)
        self._task.api('put', self._task.path, {
            [ATTR_START_ACTION]: [
                values
            ]
        })

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
        return self.raw[self.index].get(ATTR_ID)

    @property
    def transition_time(self):
        """A transition runs for this long from the time in task_start.

        Value is in seconds x 10
        """
        return self.raw.get(ATTR_TRANSITION_TIME) / 60 / 10

    @property
    def dimmer(self):
        return self.raw.get(ATTR_LIGHT_DIMMER)

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self.task
