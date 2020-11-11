import datetime
from polog.writer import Writer
from polog.levels import Levels
from polog.base_settings import BaseSettings
from polog.utils.not_none_to_dict import not_none_to_dict
from polog.utils.exception_to_dict import exception_to_dict
from polog.utils.get_traceback import get_traceback, get_locals_from_traceback


ALLOWED_TYPES = {
    'function': lambda x: type(x) is str or callable(x), # Функция, событие в которой логируется. Ожидается либо сам объект функции, либо строка с ее названием.
    'module': lambda x: type(x) is str, # Модуль, событие в котором логируется. Ожидается только название.
    'message': lambda x: type(x) is str, # Сообщение, любая строка. В таком виде будет записана в БД.
    'exception': lambda x: type(x) is str or isinstance(x, Exception), # Экземпляр перехваченного пользователем исключения или его название. Если передается экземпляр, в БД автоматически будут заполнены колонки с названием исключения и его сообщением.
    'vars': lambda x: type(x) is str, # Ожидается любая строка, но для совместимости формата с автоматическими логами рекомендуется передавать аргументы в функцию polog.utils.json_vars(), а уже то, что она вернет, передавать сюда в качестве аргумента.
    'success': lambda x: type(x) is bool, # Успех / провал операции, которая логируется.
    'level': lambda x: type(x) is str or type(x) is int,
}

CONVERT_VALUES = {
    'function': lambda x: x if isinstance(x, str) else x.__name__,
    'exception': lambda x: x if isinstance(x, str) else type(x).__name__,
    'level': Levels.get,
}

CONVERT_KEYS = {
    'vars': 'local_variables',
}

def log(*args, **kwargs):
    """
    Функция для ручного создания лога.
    Первым и единственным позиционным аргументом можно передать сообщение.
    Именованные аргументы могут быть только с именами, которые перечислены как ключи в ALLOWED_TYPES и с типами значений, которые соответствуют этим ключам.
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
        if key not in ALLOWED_TYPES:
            raise ValueError(f'Unknown argument name "{key}". Allowed arguments: {", ".join(ALLOWED_TYPES.keys())}.')
        if not ALLOWED_TYPES[key](value):
            raise ValueError(f'Type "{type(value).__name__}" is not allowed for variable "{key}".')
        if key in CONVERT_VALUES:
            value = CONVERT_VALUES[key](value)
        if key in CONVERT_KEYS:
            key = CONVERT_KEYS[key]
        not_none_to_dict(args_dict, key, value)
    if not ('level' in kwargs):
        args_dict['level'] = BaseSettings().level
    if 'exception' in kwargs:
        # Проверяем, что передано само исключение, а не его название.
        if not (type(kwargs['exception']) is str):
            exception_to_dict(args_dict, kwargs['exception'])
            args_dict['traceback'] = get_traceback()
            args_dict['local_variables'] = get_locals_from_traceback()
        args_dict['success'] = args_dict['success'] if 'success' in kwargs else False
        if not ('level' in kwargs):
            # Если передано исключение, используем уровень логирования, соответствующий ошибкам.
            args_dict['level'] = BaseSettings().errors_level
        args_dict.pop('exception')
    if 'function' in kwargs:
        # Проверяем, что передано не название функции, а она сама.
        if callable(kwargs['function']):
            args_dict['function'] = kwargs['function'].__name__
            args_dict['module'] = kwargs['function'].__module__
    args_dict['auto'] = False
    Writer().write((None, None), **args_dict)
