import datetime
import functools
from polog.core.writer import Writer
from polog.core.levels import Levels
from polog.core.settings_store import SettingsStore
from polog.core.utils.not_none_to_dict import not_none_to_dict
from polog.core.utils.exception_to_dict import exception_to_dict
from polog.core.utils.get_traceback import get_traceback, get_locals_from_traceback
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

    def _push(self, fields):
        Writer().write((None, None), **fields)


log = BaseLogger()
