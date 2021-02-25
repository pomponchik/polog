import inspect
from polog.flog import flog
from polog.core.registering_functions import RegisteringFunctions
from polog.core.utils.get_methods import get_methods as get_logging_methods, make_originals


def clog(*methods, message=None, level=1, errors_level=None):
    """
    Фабрика декораторов классов. Можно вызывать как со скобками, так и без.
    В задекорированном классе @flog() применяется ко всем методам, кроме тех, чье название начинается с '__'.
    Приоритет декорирования через класс ниже, чем при прямом декорировании метода с помощью @flog() самим пользователем. Если пользователь навесил на метод задекорированного класса еще @flog(), то применяться будет только декоратор из flog().
    """
    def decorator(Class):
        # Получаем имена методов класса.
        all_methods = get_logging_methods(Class, *methods)
        for method_name in all_methods:
            method = getattr(Class, method_name)
            # Конфигурируем декоратор для метода.
            wrapper = flog(message=message, level=level, errors_level=errors_level, is_method=True)
            # Применяем его.
            new_method = wrapper(method)
            setattr(Class, method_name, new_method)
        # Получаем кортеж с именами методов, которые логировать НЕ надо.
        # Если они уже залогированы - нужно вернуть оригиналы.
        originals = make_originals(Class, *methods)
        register = RegisteringFunctions()
        for method_name in originals:
            method = getattr(Class, method_name)
            original = register.get_original(method)
            setattr(Class, method_name, original)
        return Class
    if not len(methods):
        return decorator
    elif len(methods) == 1 and inspect.isclass(methods[0]):
        return decorator(methods[0])
    return decorator
