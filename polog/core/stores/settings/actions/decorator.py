from functools import wraps

from polog.core.utils.signature_matcher import SignatureMatcher


class ItIsNotAnActionError(ValueError):
    """
    Исключение, которое поднимается в случае, если сигнатура функции не совпадает с ожидаемой от коллбека для настроек.
    Предназначено только для использования внутри Polog, оно не должно быть видимым для пользователя.
    """
    pass

def is_action(function):
    """
    Декоратор, делающий из обычной функции коллбек, вызываемый при изменении отдельных пунктов настроек.

    Он делает 2 вещи:
    1. Проверяет сигнатуру обернутой функции и поднимает исключение (на этапе инициализации) в случае несовпадения.
    2. Оборачивает вызов коллбека в условие. Коллбек будет вызываться только при условии, что старый пункт настроек и новый - не равны.
    """
    @wraps(function)
    def wrapper(old_value, new_value, store):
        if old_value != new_value:
            return function(old_value, new_value, store)
    if not SignatureMatcher('.', '.', '.').match(function):
        raise ItIsNotAnActionError('The signature of the function you passed does not match the one expected from an action.')
    return wrapper
