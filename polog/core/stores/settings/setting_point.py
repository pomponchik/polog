from threading import Lock
from polog.errors import DoubleSettingError, AfterStartSettingError


class SettingPoint:
    def __init__(self, default, change_once=False, change_only_before_start=False, prove=None, converter=None, no_check_first_time=False):
        self.prove = prove
        if not no_check_first_time and not self.prove_value(default):
            raise ValueError('The default value did not pass the standard check.')
        self.value = default
        self.converter = converter
        self.change_once = change_once
        self.no_check_first_time = no_check_first_time
        self.change_only_before_start = change_only_before_start
        self.changed = False
        self.lock = Lock()

    def set(self, value):
        with self.lock:
            if self.changed and self.change_once:
                raise DoubleSettingError("You have already configured this option before. You can't change this option twice.")
            if self.change_only_before_start and self.store['started']:
                raise AfterStartSettingError('This item of settings can be changed only before the first log entry. The first record has already occurred.')
            if not self.prove_value(value):
                raise ValueError(f"You can't use the \"{value}\" object to change the settings in this case. Read the documentation.")
            if self.converter is not None:
                self.value = self.converter(self.value)
            self.value = value
            self.changed = True

    def get(self):
        with self.lock:
            return self.value

    def set_store_object(self, store):
        self.store = store

    def prove_value(self, value):
        return self.prove is None or self.prove(value)
