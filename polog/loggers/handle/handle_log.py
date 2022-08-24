import datetime

from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.stores.handlers import global_handlers
from polog.loggers.handle.abstract import AbstractHandleLogger
from polog.core.log_item import LogItem


class BaseLogger(AbstractHandleLogger):
    """
    Экземпляры данного класса - вызываемые объекты, каждый вызов которых означает создание лога.
    """
    # Ключи - названия полей, значения - функции.
    # Каждая из этих функций должна принимать словарь с уже ранее извлеченными значениями полей и возвращать значение поля, название которого является ключом.
    _default_values = {
        'level': lambda fields: SettingsStore()['default_level'] if fields.get('success', True) else SettingsStore()['default_error_level'],
        'time': lambda fields: datetime.datetime.now(),
    }

    def _specific_processing(self, fields):
        fields['auto'] = False
        service_name = self._settings['service_name']
        if service_name is not None:
            fields['service_name'] = service_name
        self._extract_exception(fields, change_success=True, change_level=True)
        self._extract_function_data(fields)
        self._defaults_to_dict(fields)

    def _defaults_to_dict(self, fields):
        """
        Некоторые значения являются обязательными, но от пользователя не поступили. В этом случае мы генерируем их автоматически.
        В словаре self._default_values по ключам в виде названий полей лога хранятся функции. Каждая такая функция должна принимать словарь с ранее уже извлеченными полями лога и возвращать содержимое обязательного поля.
        """
        for key, get_default in self._default_values.items():
            if key not in fields:
                fields[key] = get_default(fields)

    def _extract_function_data(self, fields):
        """
        Если пользователь передал объект функции, из него извлекаются название функции и модуль, в котором она была объявлена.
        Также пользователь может передать название функции, в этом случае никаких преобразований с ним делаться не будет.

        fields - словарь с извлеченными из переданных пользователем аргументов данными.
        """
        function = fields.get('function')
        if function is not None and callable(function):
            try:
                fields['function'] = function.__name__
            except AttributeError:
                fields['function'] = str(function)
            try:
                fields['module'] = function.__module__
            except AttributeError:
                pass

    def _push(self, fields):
        """
        Передаем словарь fields в общую очередь логов.
        Предварительно проверяем, достаточен ли уровень лога для того, чтобы это сделать.
        """
        if fields.get('level') >= self._settings['level']:
            log = LogItem()
            log.set_data(fields)
            log.set_handlers(global_handlers)
            self._engine.write(log)


handle_log = BaseLogger()
