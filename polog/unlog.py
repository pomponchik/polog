from inspect import isclass

from polog.core.stores.registering_functions import RegisteringFunctions
from polog.errors import IncorrectUseOfTheDecoratorError


def unlog_function(function):
    """
    Запрет логирования функции.

    Он достигается через внесение id функции в реестр функций, который запрещено декорировать, через класс RegisteringFunctions.
    Если функция уже была задекорирована логгером, возвращается ее оригинал, до декорирования. Класс RegisteringFunctions хранит ссылку на оригинальную версию каждой задекорированной функции и возвращает ее по запросу.
    """
    if not RegisteringFunctions().is_decorator(function):
        RegisteringFunctions().forbid(function)
        return function
    original_function = RegisteringFunctions().get_original(function)
    RegisteringFunctions().remove(function)
    RegisteringFunctions().forbid(original_function)
    return original_function

def unlog(obj):
    """
    Декоратор, запрещающий логирование внутри обернутых им функций и классов.

    Если им оборачивается класс, в нем игнорируются дандер-методы.
    """
    if isclass(obj):
        for function_name in dir(obj):
            if not function_name.startswith('__'):
                maybe_method = getattr(obj, function_name)
                if callable(maybe_method):
                    setattr(obj, function_name, unlog_function(maybe_method))
        return obj
    elif callable(obj):
        return unlog_function(obj)
    else:
        raise IncorrectUseOfTheDecoratorError('The unlogging decorator can only be used for functions and classes.')
