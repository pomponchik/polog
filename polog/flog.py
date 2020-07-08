import time
import inspect
import datetime
from functools import wraps
from polog.utils.raise_exception import raise_exception
from polog.utils.log_exception_info import log_exception_info
from polog.utils.log_normal_info import log_normal_info
from polog.utils.get_base_args_dict import get_base_args_dict


def flog(message=None, level=1, errors_level=None):
    def error_logger(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            args_dict = get_base_args_dict(func, message)
            try:
                start = time.time()
                args_dict['time'] = datetime.datetime.now()
                result = await func(*args, **kwargs)
            except Exception as e:
                finish = time.time()
                log_exception_info(e, finish, start, args_dict, errors_level, *args, **kwargs)
                raise_exception(e)
            finish = time.time()
            log_normal_info(result, finish, start, args_dict, level, *args, **kwargs)
            return result
        @wraps(func)
        def wrapper(*args, **kwargs):
            args_dict = get_base_args_dict(func, message)
            try:
                start = time.time()
                args_dict['time'] = datetime.datetime.now()
                result = func(*args, **kwargs)
            except Exception as e:
                finish = time.time()
                log_exception_info(e, finish, start, args_dict, errors_level, *args, **kwargs)
                raise_exception(e)
            finish = time.time()
            log_normal_info(result, finish, start, args_dict, level, *args, **kwargs)
            return result
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    return error_logger
