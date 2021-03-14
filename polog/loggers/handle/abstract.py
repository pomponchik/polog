import functools
from polog.core.levels import Levels
from polog.core.settings_store import SettingsStore
from polog.core.utils.not_none_to_dict import not_none_to_dict


class AbstractHandleLogger:
    """
    Базовый класс для всех "ручных" логгеров.
    Автоматизирует проверку аргументов и прочие общие моменты.
    Для создания нового ручного логгера достаточно отнаследоваться и переопределить метод ._push().
    """
    # Ключи в словаре - названия полей, значения - функции для проверки содержимого аргументов функций.
    _allowed_types = {
        'function': lambda x: type(x) is str or callable(x), # Функция, событие в которой логируется. Ожидается либо сам объект функции, либо строка с ее названием.
        'module': lambda x: type(x) is str, # Модуль, событие в котором логируется. Ожидается только название.
        'message': lambda x: type(x) is str, # Сообщение лога, любая строка.
        'exception': lambda x: type(x) is str or isinstance(x, Exception), # Экземпляр перехваченного пользователем исключения или его название. Если передается экземпляр, поля с названием исключения и его сообщением будут заполнены автоматически.
        'vars': lambda x: type(x) is str, # Ожидается любая строка, но для совместимости формата с автоматическими логами рекомендуется передавать аргументы в функцию polog.utils.json_vars(), а уже то, что она вернет, передавать сюда в качестве аргумента.
        'success': lambda x: type(x) is bool, # Успех / провал операции, которая логируется.
        'level': lambda x: type(x) is str or type(x) is int, # Уровень важности лога.
        'local_variables': lambda x: type(x) is str, # json с локальными переменными, либо строка от пользователя в свободном формате.
    }
    # Функции, изменяющие исходные аргументы функций.
    _convert_values = {
        'function': lambda x: x if isinstance(x, str) else x.__name__,
        'exception': lambda x: x if isinstance(x, str) else type(x).__name__,
        'level': Levels.get,
    }
    # Сокращения аргументов и их полные формы.
    _convert_keys = {
        'vars': 'local_variables',
        'locals': 'local_variables',
        'e': 'exception',
    }
    # Позиционные аргументы могут быть, а могут и не быть. Если они есть, будут проименованы по этой схеме.
    _position_args = {
        1: 'message',
    }
    # Ключи - названия полей, значения - функции.
    # Каждая из этих функций должна принимать словарь с уже ранее извлеченными значениями полей и возвращать значение поля, название которого является ключом.
    _default_values = {}

    def __init__(self, settings=SettingsStore()):
        self.settings = settings

    def __getattribute__(self, name):
        """
        Экземпляр класса-наследника можно вызывать как непосредственно, так и через "методы", названия которых соответствуют зарегистрированным пользователем уровням логирования.
        Если использован второй вариант, уровень логирования подставится автоматически.
        """
        if name in Levels.levels:
            return functools.partial(self, level=name)
        return object.__getattribute__(self, name)

    def __call__(self, *args, **kwargs):
        fields = {}
        self._position_args_to_dict(args, fields, self._position_args)
        self._kwargs_to_dict(kwargs, fields)
        self._extract_exception(fields)
        self._defaults_to_dict(fields)
        self._push(fields)

    def _push(self, fields):
        raise NotImplementedError

    def _defaults_to_dict(self, fields):
        """
        Некоторые значения являются обязательными, но от пользователя не поступили. В этом случае мы генерируем их автоматически.
        В словаре self._default_values по ключам в виде названий полей лога хранятся функции. Каждая такая функция должна принимать словарь с ранее уже извлеченными полями лога и возвращать содержимое обязательного поля.
        """
        for key, get_default in self._default_values.items():
            if key not in fields:
                fields[key] = get_default(fields)

    def _kwargs_to_dict(self, kwargs, destination, raise_if_collision=True):
        """
        Перекладываем kwargs в destination, попутно проверяя на соответствие критериям.
        Также при необходимости конвертируем ключи и значения в нужные форматы.

        kwargs - оригинальный словарь kwargs.
        destination - словарь, куда мы перекладываем данные из kwargs.
        raise_if_collision - указание поднять исключение в случае попытки дважды записать в destination значения по одному ключу.
        """
        for key, value in kwargs.items():
            # Приводим вариативные ключи к стандартным формам.
            key = self._convert_values.get(key, key)
            # Проверяем переданные пользователем значения.
            if key in self._allowed_types:
                prove = self._allowed_types[key]
                if not prove(value):
                    self._maybe_raise(ValueError, f'The "{key}" argument is in the wrong format.')
                    continue
            elif key in self.settings.extra_fields:
                value = str(value)
            else:
                self._maybe_raise(KeyError, f'Unknown argument name "{key}". Allowed arguments: {", ".join(self._allowed_types.keys())} and users fields.')
                continue
            # При необходимости - конвертируем переданные значения.
            value = self._convert_values.get(key, value)
            # Проверяем на коллизии.
            if key in destination and raise_if_collision:
                self._maybe_raise(ValueError, f'Duplicate information in the "{key}" field.')
                continue
            # Все проверки пройдены - сохраняем результат.
            not_none_to_dict(destination, key, value)

    def _position_args_to_dict(self, position_args, destination, channels, raise_if_empty=False):
        """
        Преобразуем позиционные аргументы исходной функции в именные, и засовываем их в словарь, где имена аргументов будут служить ключами.

        position_args - кортеж с исходными аргументами функции.
        destination - словарь, куда мы сохраняем результат.
        channels - словарь, где ключи - индексы в position_args, а значения - названия соответствующих полей.
        raise_if_empty - указание поднять исключение, если кортеж с аргументами функции пустой.
        """
        if rairaise_if_empty and not len(position_args):
            self._maybe_raise(ValueError, f'There are not enough positional arguments to call the function. {len(channels)} is expected, and 0 is given.')
        for index, name in channels.items():
            try:
                destination[name] = position_args[index]
            except IndexError:
                pass

    def _extract_exception(self, fields):
        if 'exception' in fields:
            if not (type(kwargs['exception']) is str):
                exception_to_dict(args_dict, kwargs['exception'])

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

    @staticmethod
    def _maybe_raise(exception, message):
        """
        При реальном использовании логгер не должен аффектить работу основной программы.
        Даже в случае, когда он был использован неправильно, он должен подавить возникшее исключение и по возможности залогировать хоть что-то.
        На этапе отладки наоборот, рекомендуется отключить подавление исключений, чтобы ошибки использования логгера были явными.

        Управлять режимом подавления исключений можно через config, манипулируя настройкой silent_internal_exceptions.
        """
        if not SettingsStore().silent_internal_exceptions:
            raise exception(message)
