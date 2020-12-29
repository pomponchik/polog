import time
import inspect
import datetime
from functools import wraps
from polog.utils.reraise_exception import reraise_exception
from polog.utils.log_exception_info import log_exception_info
from polog.utils.log_normal_info import log_normal_info
from polog.utils.get_base_args_dict import get_base_args_dict
from polog.registering_functions import RegisteringFunctions
from polog.errors import IncorrectUseOfTheDecoratorError
from polog.message import message as _message


def flog(*args, message=None, level=1, errors_level=None, is_method=False):
    """
    Фабрика декораторов логирования для функций. Можно вызывать как со скобками, так и без.
    """
    def error_logger(func):
        # Если функция уже ранее была задекорирована, мы декорируем ее саму, а не ее в уже задекорированном виде.
        func, before_change_func = RegisteringFunctions().get_original(func), func
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            """
            Обертка для корутин, вызов обернутой функции происходит через await.
            """
            _message.clean_context()
            args_dict = get_base_args_dict(func, message)
            try:
                start = time.time()
                args_dict['time'] = datetime.datetime.now()
                result = await func(*args, **kwargs)
            except Exception as e:
                finish = time.time()
                log_exception_info(e, finish, start, args_dict, errors_level, *args, **kwargs)
                reraise_exception(e)
            finish = time.time()
            log_normal_info(result, finish, start, args_dict, level, *args, **kwargs)
            return result
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Обертка для обычных функций.
            """
            _message.clean_context()
            args_dict = get_base_args_dict(func, message)
            try:
                start = time.time()
                args_dict['time'] = datetime.datetime.now()
                result = func(*args, **kwargs)
            except Exception as e:
                finish = time.time()
                log_exception_info(e, finish, start, args_dict, errors_level, *args, **kwargs)
                reraise_exception(e)
            finish = time.time()
            log_normal_info(result, finish, start, args_dict, level, *args, **kwargs)
            return result
        if inspect.iscoroutinefunction(func):
            result = async_wrapper
        else:
            result = wrapper
        # Проверяем, что функцию не запрещено декорировать. Если запрещено - возвращаем оригинал, иначе - какой-то из wrapper'ов.
        result = RegisteringFunctions().get_function_or_wrapper(func, before_change_func, wrapper, is_method)
        return result
    # Определяем, как вызван декоратор - как фабрика декораторов (т. е. без позиционных аргументов) или как непосредственный декоратор.
    if not len(args):
        return error_logger
    elif len(args) == 1 and callable(args[0]):
        return error_logger(args[0])
    raise IncorrectUseOfTheDecoratorError('You used the logging decorator incorrectly. Read the documentation.')
