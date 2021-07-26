def reload_engine():
    """
    Перезапуск движка Polog.

    Функция используется для обхода циклических импортов.
    """
    from polog.core.engine.engine import Engine
    Engine().reload()
