from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.stores.levels import Levels


def get_errors_level(error_level_in_function, simple_level_in_function):
    """
    Ошибка по умолчанию логируется с уровнем, который берется из глобальных настроек логгера, однако локально в конкретном декораторе это можно изменить.

    В данной функции мы смотрим, определен ли уровень логирования ошибок в конкретном декораторе. Если определен - используем его.
    Если нет - берем максимальный из трех уровней: дефолтный уровень для всех логов ('default_level' в настройках), дефолтный уровень для ошибок ('default_error_level') и уровень для всех событий, переданный в декоратор.

    Если в декоратор передано какое-то имя уровня, и оно не зарегистрировано в Polog ранее, оно игнорируется (декоратор ведет себя так, будто оно не передано).
    """
    if error_level_in_function is not None:
        try:
            return Levels.get(error_level_in_function)
        except (KeyError, ValueError):
            pass

    store = SettingsStore()

    levels_to_choose = [store['default_level'], store['default_error_level']]
    if simple_level_in_function is not None:
        try:
            levels_to_choose.append(Levels.get(simple_level_in_function))
        except (KeyError, ValueError):
            pass

    return max(levels_to_choose)
