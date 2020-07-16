import datetime
from polog.writer import Writer
from polog.levels import Levels
from polog.base_settings import BaseSettings
from polog.utils.not_none_to_dict import not_none_to_dict
from polog.utils.exception_to_dict import exception_to_dict


ALLOWED_TYPES = {
    'function': (str, type(lambda: None)), # Функция, событие в которой логируется. Ожидается либо сам объект функции, либо строка с ее названием.
    'module': (str, ), # Модуль, событие в котором логируется. Ожидается только название.
    'message': (str, ), # Сообщение, любая строка. В таком виде будет записана в БД.
    'exception': (str, Exception), # Экземпляр перехваченного пользователем исключения или его название. Если передается экземпляр, в БД автоматически будут заполнены колонки с названием исключения и его сообщением.
    'vars': (str, ), # Ожидается любая строка, но для совместимости формата с автоматическими логами рекомендуется передавать аргументы в функцию polog.utils.json_vars(), а уже то, что она вернет, передавать сюда в качестве аргумента.
    'success': (bool, ), # Успех / провал операции, которая логируется.
}

CONVERT_VALUES = {
    'function': lambda x: x if isinstance(x, str) else x.__name__,
    'exception': lambda x: x if isinstance(x, str) else type(x).__name__,
}

CONVERT_KEYS = {
    'vars': 'input_variables',
}

def log(*args, **kwargs):
    """
    Функция для ручного создания лога.
    Первым и единственным позиционным аргументом можно передать уровень логирования. Если не передать - по умолчанию будет использован уровень 1.
    Именованные аргументы могут быть только с именами, которые перечислены как ключи в ALLOWED_TYPES и с типами значений, которые соответствуют этим ключам.
    Именованный аргумент 'vars' соответствует колонке в базе данных 'input_variables', куда пишутся входные аргументы функций. Чтобы сгенерировать правильную строку для заполнения этого поля, желательно использовать функцию polog.utils.json_vars(), куда можно передать любые аргументы и получить в результате json с ними.
    Не обязательно передавать сюда все возможные именованные аргументы. Передавать нужно только то, что нужно залогировать, именно поэтому они не заданы жестко в данном случае.
    """
    args_dict = {}
    if len(args) == 0:
        args_dict['level'] = 1
    elif len(args) == 1:
        args_dict['level'] = Levels.get(args[0])
    else:
        raise ValueError('A maximum of 1 positional argument is expected. Only the logging level can be passed as a positional argument.')

    args_dict['time'] = datetime.datetime.now()
    for key, value in kwargs.items():
        if key not in ALLOWED_TYPES:
            raise ValueError(f'Unknown argument name "{key}". Allowed arguments: {ALLOWED_TYPES}.')
        is_allowed = sum([isinstance(value, one) for one in ALLOWED_TYPES[key]])
        if not is_allowed:
            raise ValueError(f'Type "{type(value).__name__}" is not allowed for variable "{key}". Allowed types: {ALLOWED_TYPES[key]}.')
        if key in CONVERT_VALUES:
            value = CONVERT_VALUES[key](value)
        not_none_to_dict(args_dict, key, value)
    if 'exception' in kwargs:
        # Проверяем, что передано само исключение, а не его название.
        if not (type(kwargs['exception']) is str):
            exception_to_dict(args_dict, kwargs['exception'])
        args_dict['success'] = args_dict['success'] if 'success' in kwargs else False
        if not len(args):
            # Если передано исключение, используем уровень логирования, соответствующий ошибкам.
            args_dict['level'] = BaseSettings().errors_level
    if 'function' in kwargs:
        # Проверяем, что передано не название функции, а она сама.
        if isinstance(kwargs['function'], ALLOWED_TYPES['function'][1]):
            args_dict['function'] = kwargs['function'].__name__
            args_dict['module'] = kwargs['function'].__module__
    args_dict['auto'] = False
    Writer().write(**args_dict)
