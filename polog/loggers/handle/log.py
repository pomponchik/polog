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

    def __call__(self, *args, **kwargs):
        """
        Ручное создание лога.

        Первым и единственным позиционным аргументом можно передать сообщение.
        Именованные аргументы могут быть только с именами, которые перечислены как ключи в _allowed_types и с типами значений, которые соответствуют этим ключам.
        Именованный аргумент 'vars' соответствует переменной 'input_variables', передаваемой в обработчики, туда пишутся входные аргументы функций. Чтобы сгенерировать правильную строку для заполнения этого поля, желательно использовать функцию polog.utils.json_vars(), куда можно передать любые аргументы и получить в результате json с ними.
        Не обязательно передавать сюда все возможные именованные аргументы. Передавать нужно только то, что нужно залогировать, именно поэтому они не заданы жестко в данном случае.
        """
        args_dict = {}
        if len(args) == 1:
            args_dict['message'] = str(args[0])
        elif len(args) > 1:
            raise ValueError('A maximum of 1 positional argument is expected. Only the logging message can be passed as a positional argument.')

        args_dict['time'] = datetime.datetime.now()
        for key, value in kwargs.items():
            if key not in self._allowed_types:
                if key in self.settings.extra_fields:
                    args_dict[key] = str(value)
                else:
                    raise KeyError(f'Unknown argument name "{key}". Allowed arguments: {", ".join(self._allowed_types.keys())} and users fields.')
            else:
                if not self._allowed_types[key](value):
                    raise ValueError(f'Type "{type(value).__name__}" is not allowed for variable "{key}".')
                if key in self._convert_values:
                    value = self._convert_values[key](value)
                if key in self._convert_keys:
                    key = self._convert_keys[key]
            not_none_to_dict(args_dict, key, value)
        if not ('level' in kwargs):
            args_dict['level'] = self.settings.level
        if 'exception' in kwargs:
            # Проверяем, что передано само исключение, а не его название.
            if not (type(kwargs['exception']) is str):
                exception_to_dict(args_dict, kwargs['exception'])
                args_dict['traceback'] = get_traceback()
                args_dict['local_variables'] = get_locals_from_traceback()
            args_dict['success'] = args_dict['success'] if 'success' in kwargs else False
            if not ('level' in kwargs):
                # Если передано исключение, используем уровень логирования, соответствующий ошибкам.
                args_dict['level'] = self.settings.errors_level
            args_dict.pop('exception')
        if 'function' in kwargs:
            # Проверяем, что передано не название функции, а она сама.
            if callable(kwargs['function']):
                args_dict['function'] = kwargs['function'].__name__
                args_dict['module'] = kwargs['function'].__module__
        args_dict['auto'] = False
        # TODO: переписать это говно нормально.
        Writer().write((None, None), **args_dict)


log = BaseLogger()
