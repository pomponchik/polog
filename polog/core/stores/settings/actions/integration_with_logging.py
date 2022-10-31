import logging
import traceback
from datetime import datetime

from polog.core.stores.settings.actions.decorator import is_action


def from_logging_filter_to_polog(record):
    """
    Здесь копируется информация из объекта записи logging и передается логгеру Polog.
    """
    from polog.loggers.handle.handle_log import simple_handle_log
    from polog.core.stores.settings.settings_store import SettingsStore


    store = SettingsStore()
    data = {}

    data['time'] = datetime.fromtimestamp(record.created)
    if record.msg:
        data['message'] = record.getMessage()
    data['level'] = record.levelno
    if record.levelno >= 30:
        data['success'] = False
    else:
        data['success'] = True
    data['module'] = record.module
    data['line_number'] = record.lineno
    if record.funcName.isidentifier():
        data['function'] = record.funcName
    data['path_to_code'] = record.pathname
    if record.exc_info is not None:
        data['exception_type'] = record.exc_info[0].__name__
        data['traceback'] = store['json_module'].dumps(traceback.format_tb(record.exc_info[2]))
        data['exception_message'] = str(record.exc_info[1])
    data['thread'] = f'{record.threadName} ({record.thread})'
    data['process'] = f'{record.processName} ({record.process})'

    data['from_logging'] = True

    simple_handle_log(**data)
    return not store['logging_off']

@is_action
def integration_with_logging(old_value, new_value, store):
    """
    Включаем / выключаем интеграцию с модулем logging из стандартной библиотеки.

    Интеграция работает через навешивание фильтра на корневой регистратор, который всегда возвращает True, но при этом копирует содержимое запись в Polog.
    При этом не происходит никаких модификаций логики работы модуля logging. Если там настроены свои обработчики и прочая инфраструктура, они продолжат работать параллельно с Polog и независимо от него.
    """
    if new_value:
        logging.root.addFilter(from_logging_filter_to_polog)
    else:
        logging.root.removeFilter(from_logging_filter_to_polog)
