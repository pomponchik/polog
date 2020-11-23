from polog.writer import Writer
from polog.base_settings import BaseSettings
from polog.levels import Levels
from polog.utils.json_vars import json_vars
from polog.message import message


def log_normal_info(result, finish, start, args_dict, level, *args, **kwargs):
    """
    Автоматическое логирование в нормальном случае, когда ошибки не произошло.
    """
    level = Levels.get(level)
    if level >= BaseSettings().level:
        args_dict['success'] = True
        args_dict['result'] = str(result)
        args_dict['time_of_work'] = finish - start
        args_dict['level'] = level
        message.copy_context(args_dict)
        input_variables = json_vars(*args, **kwargs)
        if not (input_variables is None):
            args_dict['input_variables'] = input_variables
        Writer().write((args, kwargs), **args_dict)
