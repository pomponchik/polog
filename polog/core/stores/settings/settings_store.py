from threading import Lock
from polog.core.utils.read_only_singleton import ReadOnlySingleton
from polog.core.stores.settings.setting_point import SettingPoint
from polog.core.stores.levels import Levels


class SettingsStore(ReadOnlySingleton):
    """
    Здесь хранятся все базовые настройки Polog.
    Данный класс не предназначен для доступа "снаружи". Его должны использовать только другие части Polog.
    """

    points = {
        'pool_size': SettingPoint(2, prove=lambda x: isinstance(x, int) and x > 0),
        'original_exceptions': SettingPoint(False, prove=lambda x: isinstance(x, bool)),
        'level': SettingPoint(1, prove=lambda x: (isinstance(x, int) and x > 0) or isinstance(x, str), converter=Levels.get),
        'errors_level': SettingPoint(2, prove=lambda x: (isinstance(x, int) and x > 0) or isinstance(x, str), converter=Levels.get),
        'service_name': SettingPoint('base', prove=lambda x: isinstance(x, str) and x.isidentifier()),
        'delay_before_exit': SettingPoint(1.0, prove=lambda x: (isinstance(x, int) or isinstance(x, float)) and x >= 0),
        'silent_internal_exceptions': SettingPoint(False, prove=lambda x: isinstance(x, bool)),
        'started': SettingPoint(False, prove=lambda x: isinstance(x, bool) and x == True, no_check_first_time=True),
    }
    points_are_informed = False
    handlers = {}
    extra_fields = {}

    def __init__(self, **kwargs):
        with Lock():
            if not self.points_are_informed:
                for name, point in self.points.items():
                    point.set_store_object(self)
                self.points_are_informed = True

    def __getitem__(self, key):
        if key not in self.points:
            raise KeyError()
        point = self.points[key]
        value = point.get()
        return value

    def __setitem__(self, key, value):
        if key not in self.points:
            raise KeyError()
        point = self.points[key]
        point.set(value)
