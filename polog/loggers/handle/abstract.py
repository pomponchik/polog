import functools
from polog.core.levels import Levels
from polog.core.settings_store import SettingsStore
from polog.core.utils.not_none_to_dict import not_none_to_dict
from polog.core.utils.exception_to_dict import exception_to_dict
from polog.core.utils.get_traceback import get_traceback, get_locals_from_traceback


class AbstractHandleLogger:
    """
    Базовый класс для всех "ручных" логгеров.
    Автоматизирует проверку аргументов и прочие общие моменты.

    Для создания нового ручного логгера достаточно отнаследоваться и переопределить метод ._push().
    Также необходимо переопределить ._specific_processing(), если извлеченным полям лога требуется какая-то дополнительная обработка.
    Переопределив словарь ._default_values, можно изменить набор полей, значения к которым проставляются автоматически.

    Добавляя любые методы или атрибуты в классы-наследники, важно использовать для них имена, начинающиеся на "_".
    Это связано с тем, что у каждого объекта отнаследованного класса можно вызывать методы, имена которых соответствуют уровням логирования. Поэтому приходится следить, чтобы случайно не возникло коллизии имен между именами уровней логирования (им запрещено начинаться на "_") и методами, которые предоставляет класс.
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
        'level': Levels.get,
    }
    # Сокращения аргументов и их полные формы.
    _convert_keys = {
        'vars': 'local_variables',
        'locals': 'local_variables',
        'e': 'exception',
    }
    # Позиционные аргументы могут быть, а могут и не быть. Если они есть, будут проименованы по этой схеме.
    # Ключи - номера аргументов (отсчет идет с 0), значения - названия полей.
    _position_args = {
        0: 'message',
    }
    # Ключи - названия полей, значения - функции.
    # Каждая из этих функций должна принимать словарь с уже ранее извлеченными значениями полей и возвращать значение поля, название которого является ключом.
    _default_values = {}
    # Множество названий полей, которые запрещено логировать.
    # Данное множество просматривается в приоритете по сравнению с разрешенными полями и блокирует запись в том числе запрещенных позиционных аргументов.
    _forbidden_fields = set()

    def __init__(self, settings=SettingsStore()):
        self._settings = settings

    def __getattribute__(self, name):
        """
        Экземпляр класса-наследника можно вызывать как непосредственно, так и через "методы", названия которых соответствуют зарегистрированным пользователем уровням логирования.
        Если использован второй вариант, уровень логирования подставится автоматически.
        """
        if name in Levels.levels:
            return functools.partial(self, level=name)
        return object.__getattribute__(self, name)

    def __call__(self, *args, **kwargs):
        """
        Каждый вызов объекта отнаследованного класса как функции подразумевает выполнение трех действий:

        1. Извлечение данных из переданных пользователем аргументов (каких угодно) в словарь. Попутно данные проверяются на соответствие ожидаемым форматам, и, возможно, как-то еще дополнительно обрабатываются.
        2. Применение каких-то специфических методов к полученному словарю с данными для его преобразования. Набор этих методов определяется в классе-наследнике, их может вообще не быть.
        3. Передача полученного словаря с данными куда-то, где с ним будет сделано что-то. Конкретное действие определяется в классе-наследнике.
        """
        fields = self._prepare_data(args, kwargs)
        self._specific_processing(fields)
        self._push(fields)

    def _push(self, fields):
        """
        Единственный метод, который обязательно переопределять в отнаследованных классах.
        Здесь словарь с данными, собранный из переданных пользователем аргументов, куда-то передается.

        fields - словарь с извлеченными полями лога.
        """
        raise NotImplementedError

    def _specific_processing(self, fields):
        """
        Данный метод необходимо переопределить, если данные лога недостаточно просто извлечь из аргументов, переданных пользователем, а с ними дополнительно что-то нужно сделать.
        Например взять объект из одного поля, извлечь из него какие-то данные и заполнить несколько других полей.
        Метод не должен ничего возвращать, он работает со словарем, переданным в него как аргумент.

        fields - словарь с извлеченными полями лога.
        """
        pass

    def _prepare_data(self, args, kwargs):
        """
        Извлечение базовой информации из переданных пользователем аргументов.

        args - кортеж с позиционными аргументами, переданными пользователем.
        kwargs - словарь с именованными аргументами, переданными пользователем.
        """
        fields = {}
        self._position_args_to_dict(args, fields, self._position_args)
        self._kwargs_to_dict(kwargs, fields)
        self._defaults_to_dict(fields)
        return fields

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
            key = self._convert_keys.get(key, key)
            # Проверяем, что переданное поле не запрещено использовать.
            if key in self._forbidden_fields:
                self._maybe_raise(KeyError, f'You cannot manually set the "{key}" field.')
                continue
            # Проверяем переданные пользователем значения.
            if key in self._allowed_types:
                prove = self._allowed_types[key]
                if not prove(value):
                    self._maybe_raise(ValueError, f'The "{key}" argument is in the wrong format.')
                    continue
            elif key in self._settings.extra_fields:
                value = str(value)
            else:
                self._maybe_raise(KeyError, f'Unknown argument name "{key}". Allowed arguments: {", ".join(self._allowed_types.keys())} and users fields.')
                continue
            # При необходимости - конвертируем переданные значения.
            if key in self._convert_values:
                value = self._convert_values.get(key)(value)
            # Проверяем на коллизии.
            if key in destination and raise_if_collision:
                self._maybe_raise(ValueError, f'Duplicate information in the "{key}" field.')
                continue
            # Все проверки пройдены - сохраняем результат.
            not_none_to_dict(destination, key, value)

    def _position_args_to_dict(self, position_args, destination, channels, raise_if_empty=False, raise_if_very_busy=True):
        """
        Преобразуем позиционные аргументы исходной функции в именные, и засовываем их в словарь, где имена аргументов будут служить ключами.

        position_args - кортеж с исходными аргументами функции.
        destination - словарь, куда мы сохраняем результат.
        channels - словарь, где ключи - индексы в position_args, а значения - названия соответствующих полей.
        raise_if_empty - указание поднять исключение, если кортеж с аргументами функции пустой.
        """
        if raise_if_empty and not len(position_args):
            self._maybe_raise(ValueError, f'There are not enough positional arguments to call the function. {len(channels)} is expected, and 0 is given.')
        if len(position_args) > len(channels) and raise_if_very_busy:
            self._maybe_raise(ValueError, 'Too many positional function arguments.')
        for index, name in channels.items():
            if name in self._forbidden_fields:
                self._maybe_raise(KeyError, f'You cannot manually set the "{name}" field as a positional argument.')
            try:
                destination[name] = position_args[index]
            except IndexError:
                pass

    def _extract_exception(self, fields, change_success=False, change_level=False):
        """
        Если передан экземпляр исключения, здесь из него извлекается вся необходимая информация:

        1. Название исключения.
        2. Сообщение, переданное в исключении.
        3. Трейсбек.
        4. Локальные переменные.

        Аргументы:
        fields - исходный словарь с полями лога. Исключение может в нем лежать по ключу 'exception'.
        change_success - флаг, сообщающий о том, нужно ли автоматически проставлять метку success лога в значение False, если пользователем передано исключение.
        change_level - еще один флаг. Сообщает, нужно ли устанавливать уровень логирования на соответствующий ошибкам в случае, когда передано исключение.
        """
        if 'exception' in fields:
            if isinstance(fields['exception'], Exception):
                exception_to_dict(fields, fields['exception'])
                fields['traceback'] = get_traceback()
                fields['local_variables'] = get_locals_from_traceback()
            elif isinstance(fields['exception'], str):
                fields['exception_type'] = fields['exception']
            fields.pop('exception')
            if change_success:
                fields['success'] = False
            if change_level and not ('level' in fields):
                fields['level'] = self._settings.errors_level

    @staticmethod
    def _maybe_raise(exception, message):
        """
        При реальном использовании логгер не должен аффектить работу основной программы.
        Даже в случае, когда он был использован неправильно, он должен подавить возникшее исключение и по возможности залогировать хоть что-то.
        На этапе отладки наоборот, рекомендуется отключить подавление исключений, чтобы ошибки использования логгера были явными.

        Управлять режимом подавления исключений можно через config(), манипулируя настройкой silent_internal_exceptions.

        exception - класс исключения, которое может быть поднято.
        message - сообщение, с которым исключение exception может быть поднято.
        """
        if not SettingsStore().silent_internal_exceptions:
            raise exception(message)
