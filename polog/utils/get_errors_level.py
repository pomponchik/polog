from polog.base_settings import BaseSettings
from polog.levels import Levels


def get_errors_level(default_in_function):
    if default_in_function is None:
        return BaseSettings().errors_level
    return Levels.get(default_in_function)
