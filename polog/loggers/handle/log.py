import datetime
from polog.core.writer import Writer
from polog.core.settings_store import SettingsStore
from polog.loggers.handle.abstract import AbstractHandleLogger


class BaseLogger(AbstractHandleLogger):
    """
    Экземпляры данного класса - вызываемые объекты, каждый вызов которых означает создание лога.
    """
    _default_values = {
        'level': lambda fields: SettingsStore().level if fields.get('success', True) else SettingsStore().errors_level,
        'time': lambda fields: datetime.datetime.now(),
    }

    def _specific_processing(self, fields):
        fields['auto'] = False
        self._extract_exception(fields, change_success=True, change_level=True)
        self._extract_function_data(fields)

    def _extract_function_data(self, fields):
        function = fields.get('function')
        if function is not None and callable(function):
            fields['function'] = function.__name__
            fields['module'] = function.__module__

    def _push(self, fields):
        Writer().write((None, None), **fields)


log = BaseLogger()
