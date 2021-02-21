from polog.core.writer import Writer
from polog.core.base_settings import BaseSettings
from polog.errors import LoggedError
from polog.core.utils.get_traceback import get_traceback, get_locals_from_traceback
from polog.core.utils.get_errors_level import get_errors_level
from polog.utils.json_vars import json_vars
from polog.core.utils.exception_to_dict import exception_to_dict
from polog.core.utils.extract_extra_fields import extract_extra_fields
from polog.message import message


def log_exception_info(exc, finish, start, args_dict, errors_level, *args, **kwargs):
    """
    Автоматическое логирование в случае ошибки.
    """
    exc_type = type(exc)
    if not (exc_type is LoggedError):
        errors_level = get_errors_level(errors_level)
        if errors_level >= BaseSettings().level:
            exception_to_dict(args_dict, exc)
            args_dict['success'] = False
            args_dict['traceback'] = get_traceback()
            args_dict['local_variables'] = get_locals_from_traceback()
            args_dict['time_of_work'] = finish - start
            args_dict['level'] = errors_level
            input_variables = json_vars(*args, **kwargs)
            message.copy_context(args_dict)
            message.clean_context()
            if not (input_variables is None):
                args_dict['input_variables'] = input_variables
            extract_extra_fields((args, kwargs), args_dict)
            Writer().write((args, kwargs), **args_dict)
