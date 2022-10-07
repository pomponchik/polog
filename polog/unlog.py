from inspect import isclass
from contextvars import ContextVar
from functools import wraps
from dataclasses import dataclass
from typing import Optional
from inspect import iscoroutinefunction

from polog.core.stores.registering_functions import RegisteringFunctions
from polog.errors import IncorrectUseOfTheDecoratorError
from polog.core.stores.settings.settings_store import SettingsStore


context = ContextVar('unlog')


@dataclass
class UnlogOrder:
    full: Optional[bool]

def get_unlog_status():
    store = SettingsStore()
    status = context.get(None)

    if status is None:
        return False

    if status.full is None:
        return store['full_unlog']

    return status.full

def set_unlogged(function, full):
    print('input:', function)
    @wraps(function)
    def wrapper(*args, **kwargs):
        context.set(UnlogOrder(full=full))
        try:
            print('in the wrapper:', function)
            return function(*args, **kwargs)
        finally:
            context.set(None)
    @wraps(function)
    async def async_wrapper(*args, **kwargs):
        context.set(UnlogOrder(full=full))
        try:
            return await function(*args, **kwargs)
        finally:
            context.set(None)
    if iscoroutinefunction(function):
        print('return 1')
        return async_wrapper
    print('return 2', wrapper)
    return wrapper

def unlog_function(function, full):
    """
    Запрет логирования функции.

    Он достигается через внесение id функции в реестр функций, который запрещено декорировать, через класс RegisteringFunctions.
    Если функция уже была задекорирована логгером, возвращается ее оригинал, до декорирования. Класс RegisteringFunctions хранит ссылку на оригинальную версию каждой задекорированной функции и возвращает ее по запросу.
    """
    print('function:', function)
    if not RegisteringFunctions().is_decorator(function):
        print('path 1')
        RegisteringFunctions().forbid(function)
        result = function
    else:
        print('path 2')
        original_function = RegisteringFunctions().get_original(function)
        RegisteringFunctions().remove(function)
        RegisteringFunctions().forbid(original_function)
        result = original_function
    print('function after:', function)
    print('after all result:', result)

    wrapped_result = set_unlogged(result, full)
    print('function after 2:', function, wrapped_result)
    RegisteringFunctions().add_unlogged(wrapped_result, result)
    print('function after 3:', function, wrapped_result)
    return wrapped_result

def unlog(*args, full=None):
    """
    Фабрика декораторов, запрещающих логирование внутри обернутых ими функций и классов.

    Если декоратором оборачивается класс, в нем игнорируются дандер-методы.
    """
    def decorator(obj):
        if isclass(obj):
            for function_name in dir(obj):
                if not function_name.startswith('__'):
                    maybe_method = getattr(obj, function_name)
                    if callable(maybe_method):
                        setattr(obj, function_name, unlog_function(maybe_method, full))
            return obj
        elif callable(obj):
            return unlog_function(obj, full)
        else:
            raise IncorrectUseOfTheDecoratorError('The unlogging decorator can only be used for functions and classes.')

    if len(args) == 1:
        return decorator(args[0])
    elif not args:
        return decorator
    else:
        raise IncorrectUseOfTheDecoratorError('The unlogging decorator can only be used for functions and classes, without any other addictional arguments.')
