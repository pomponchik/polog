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

class UnlogDecorator:
    def __init__(self):
        self.store = SettingsStore()

    def __call__(self, *args, full=None):
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
                            setattr(obj, function_name, self.unlog_function(maybe_method, full))
                return obj
            elif callable(obj):
                return self.unlog_function(obj, full)
            else:
                raise IncorrectUseOfTheDecoratorError('The unlogging decorator can only be used for functions and classes.')

        if len(args) == 1:
            return decorator(args[0])
        elif not args:
            return decorator
        else:
            raise IncorrectUseOfTheDecoratorError('The unlogging decorator can only be used for functions and classes, without any other addictional arguments.')

    def __neg__(self):
        """
        При отрицании декоратора @unlog он возвращает log().
        Это нужно для симметрии, поскольку -log возвращает @unlog.
        """
        from polog import log

        return log

    def unlog_function(self, function, full):
        """
        Запрет логирования функции.

        Он достигается через внесение id функции в реестр функций, который запрещено декорировать, через класс RegisteringFunctions.
        Если функция уже была задекорирована логгером, возвращается ее оригинал, до декорирования. Класс RegisteringFunctions хранит ссылку на оригинальную версию каждой задекорированной функции и возвращает ее по запросу.
        """
        if not RegisteringFunctions().is_decorator(function):
            RegisteringFunctions().forbid(function)
            result = function
        else:
            original_function = RegisteringFunctions().get_original(function)
            RegisteringFunctions().remove(function)
            RegisteringFunctions().forbid(original_function)
            result = original_function

        wrapped_result = self.set_unlogged(result, full)
        RegisteringFunctions().add_unlogged(wrapped_result, result)
        return wrapped_result

    def get_unlog_status(self):
        """
        В этом методе решается, позволительно ли в данный момент логирование.
        """
        status = context.get(None)

        if status is None:
            return False

        if status.full is None:
            return self.store['full_unlog']

        return status.full

    def set_unlogged(self, function, full):
        @wraps(function)
        def wrapper(*args, **kwargs):
            context.set(UnlogOrder(full=full))
            try:
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
            return async_wrapper
        return wrapper


unlog = UnlogDecorator()
