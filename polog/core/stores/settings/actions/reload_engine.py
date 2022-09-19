from polog.core.stores.settings.actions.decorator import is_action


@is_action
def reload_engine(old_value, new_value, store):
    """
    Перезапуск движка Polog.

    Функция используется для обхода циклических импортов.
    """
    from polog.core.engine.engine import Engine
    Engine().reload()
