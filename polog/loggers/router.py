import inspect
from contextvars import ContextVar

from polog.core.stores.levels import Levels
from polog.loggers.handle.handle_log import handle_log
from polog.loggers.handle.message import message
from polog.loggers.auto.class_logger import clog
from polog.loggers.auto.function_logger import flog
from polog.errors import IncorrectUseLoggerError, IncorrectUseOfTheContextManagerError
from polog.loggers.finalizer import LoggerRouteFinalizer
from polog.loggers.partial import RouterPartial
from polog.unlog import unlog


contexts = ContextVar('router_contexts')


class Router:
    """
    Данный класс перенаправляет запросы к различным функциям / декораторам Polog.
    Он представляет единый интерфейс для всех логгеров.
    """
    def __call__(self, *args, **kwargs):
        """
        При вызове объекта класса, происходит определение контекста по различным признакам и перенаправление вызова в конкретный логгер. Определение происходит по двум базовым признакам:

        1. Какие аргументы были переданы на вход в функцию.
        2. Каков был жизненный цикл объекта, который она вернула.

        Исходя из ответов на эти вопросы, функция старается выяснить, в каком контексте она была вызвана. Существует 7 базовых способов вызвать объект роутера:

        1. Как обычный ручной логгер. При этом строка с сообщением должна идти первым неименованным аргументом.

        >>> log('some text')

        Этот способ может работать неправильно при использовании через REPL. Это связано с особенностью реализации: при определении контекста, в котором вызывалась функция log, используется отслеживание жизненного цикла возвращаемого значения функции. Запись происходит при обнулении счетчика ссылок на этот объект. В REPL же последнее возвращенное значение сохраняется в переменной _, то есть счетчик ссылок обнулится и лог запишется, когда код в следующей строке перезапишет _.

        2. В качестве декоратора для функции без скобок.

        >>> @log
        >>> def function():
        >>> ... pass

        3. В качестве декоратора для функции с передачей произвольных аргументов через скобки (скобки могут остаться пустыми).

        >>> @log('some text', level=5)
        >>> def function():
        >>> ... pass

        4. В качестве декоратора классов без скобок.

        >>> @log
        >>> class SomeClass:
        >>> ... pass

        5. В качестве декоратора классов с аргументами в скобках (скобки могут остаться пустыми).

        >>> @log('some text', level=5)
        >>> class SomeClass:
        >>> ... pass

        6. В качестве контекстного менеджера без скобок.

        >>> with log:
        >>> ... pass

        7. В качестве контекстного менеджера с аргументами в скобках (скобки могут остаться пустыми).

        >>> with log('some text', level=5):
        >>> ... pass

        Неправильный вызов объекта может привести к поднятию исключения, которое нельзя отключить, управляя настройкой "silent_internal_exceptions".
        Это связано с тем, что иногда невозможно определить, был вызов осуществлен как функции или как декоратора, в то время как настройка "silent_internal_exceptions" не должна гасить исключения, возникающие при инициализации декораторов.
        """
        if len(args) == 1:
            item = args[0]
            if isinstance(item, str):
                return LoggerRouteFinalizer(*args, **kwargs)
            elif inspect.isclass(item):
                return self._wrap(clog, item, *([*args][1:]), **kwargs)
            elif callable(item):
                return self._wrap(flog, item, *([*args][1:]), **kwargs)
            else:
                raise IncorrectUseLoggerError(f'The first argument of class {type(item).__name__} is not recognized.')
        elif len(args) == 0:
            return self._route_wrapper(*args, **kwargs)
        else:
            raise IncorrectUseLoggerError('Passing more than one positional argument to the logger.')

    def _route_wrapper(self, *args, **kwargs):
        """
        Декорируем декоратор.
        Когда пользователь использует синтаксис декоратора (@) со скобками, возвращается функция, которая в свою очередь вернет уже обернутую оригинальную функцию или класс.
        Так вот, в данном случае мы не просто возвращаем ее, мы возвращаем обертку, которая смотрит на то, передан в нее класс или функция, и в зависимости от этого возвращает разную обертку.
        Если вы это прочитали, соболезную.
        """
        def wrapper(item):
            if inspect.isclass(item):
                wrapped_wrapper = clog(*args, **kwargs)
            elif callable(item):
                wrapped_wrapper = flog(*args, **kwargs)
            return wrapped_wrapper(item)
        return wrapper

    def _wrap(self, wrapper, item, *args, **kwargs):
        """
        Обычно данный метод будет срабатывать, когда объект используется в качестве декоратора без скобок.
        В этом случае мы просто передаем в обертку wrapper переданный нам объект item (класс или функция) и возвращаем результат.
        Предварительно проверяем на наличие аргов и кваргов, т. к. возможна переадресация из self.__getattribute__() с обогащением доп. аргументами.
        """
        if args or kwargs:
            wrapper = wrapper(*args, **kwargs)
        return wrapper(item)

    def message(self, *args, **kwargs):
        """
        Чтобы не импортировать каждый раз лишний логгер, пользователь может вызывать объект message непосредственно от объекта класса Router.
        """
        message(*args, **kwargs)

    def suppress(self, *exceptions):
        context = RouterPartial(self)
        context.aware_calling_method('suppress', *exceptions)
        return context

    def __getattribute__(self, name):
        """
        Объект данного класса можно вызывать как непосредственно, так и через "виртуальные" методы, имена которых соответствуют именам зарегистрированных пользователем уровней логирования.
        Во втором случае вызов будет автоматически преобразован в обычный, но с добавлением аргумента "level", соответствующего имени уровня логирования, которое было использовано при вызове.
        Если пользователь при вызове с именем уровня логирования через точку еще отдельно передаст именованный аргумент level, приоритет будет у переданного аргумента.
        """
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return RouterPartial(self, level=name)

    def __neg__(self):
        """
        При отрицании объекта роутера он возвращает @unlog.
        """
        return unlog

    def __enter__(self):
        """
        Вход в объект роутера как в контекстный менеджер.

        Поскольку сам по себе роутер не может хранить состояние (он общий на всю программу и допускает параллельный доступ из нескольких потоков / корутин), оно хранится в контекстной переменной в виде стека. Это также позволяет вкладывать контексты друг в друга.
        """
        finalizer = LoggerRouteFinalizer()

        context_stack = contexts.get(None)
        if context_stack is None:
            contexts.set([finalizer])
        else:
            context_stack.append(finalizer)

        return finalizer.__enter__()

    def __exit__(self, exception_type, exception_value, traceback_instance):
        """
        Выход из контекста.
        """
        finalizers = contexts.get(None)

        if finalizers is None:
            raise IncorrectUseOfTheContextManagerError()

        finalizer = finalizers.pop()

        if not finalizers:
            contexts.set(None)

        result = finalizer.__exit__(exception_type, exception_value, traceback_instance)
        return result


log = Router()
