from polog.core.base_settings import BaseSettings
from polog.core.levels import Levels


def get_errors_level(default_in_function):
    """
    Ошибка по умолчанию логируется с уровнем, который указан в настройках как errors_level.
    В конкретном декораторе можно указать иной уровень логирования для ошибок.
    В данной функции мы смотрим, определен ли уровень логирования ошибок в конкретном декораторе. Если определен - используем его, иначе берем умолчание из класса настроек.
    Если название уровня не было ранее зарегистрировано в Polog, используется дефолтный уровень.
    """
    if default_in_function is None:
        return BaseSettings().errors_level
    try:
        return Levels.get(default_in_function)
    except KeyError:
        return BaseSettings().errors_level
