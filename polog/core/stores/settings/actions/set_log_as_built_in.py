import builtins
from contextlib import suppress
from polog.core.stores.settings.actions.decorator import is_action


@is_action
def set_log_as_built_in(old_value, new_value, store):
    """
    Устанавливаем функцию log() в качестве системной.
    После этого ее можно будет использовать из любого места программы без дополнительного импорта.
    """
    if new_value is True:
        from polog import log
        builtins.log = log
    else:
        with suppress(AttributeError):
            delattr(builtins, 'log')
