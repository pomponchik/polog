import weakref
import inspect
import traceback
from time import time
import json
from datetime import datetime

from polog.loggers.handle.handle_log import simple_handle_log
from polog.loggers.auto.class_logger import clog
from polog.loggers.auto.function_logger import flog
from polog.errors import IncorrectUseLoggerError, IncorrectUseOfTheDecoratorError, IncorrectUseOfTheContextManagerError
from polog.core.stores.settings.settings_store import SettingsStore


class LoggerRouteFinalizer:
    """
    Промежуточный объект логгера. Его задача - определить контекст, в котором был вызван роутер, и перенаправить вызов в соответствующий логгер.

    Определение контекста происходит по использованию объекта. Тут существуют несколько вариантов:
    1. Объект LoggerRouteFinalizer удаляется интерпретатором без использования. Это значит, что роутер был использован для ручного логирования, в этом случае аргументы надо передать ручному логгеру.
    2. Объект LoggerRouteFinalizer вызывается как функция, куда передается функция или класс. Это значит, что роутер был использован в качестве декоратора. Необходимо задекорировать переданный объект соответствующим декоратором (в зависимости от того, функция это или класс) и вернуть ее в таком виде.
    3. У объекта LoggerRouteFinalizer вызывается магический метод __enter__(). Это значит, что роутер используется как фабрика контекстного менеджера, необходиимо отработать соответствующим образом.
    """
    def __init__(self, *args, **kwargs):
        self.settings = SettingsStore()
        self.data = self.convert_arguments_to_dict(*args, **kwargs)
        self.finalizer = weakref.finalize(self, self.create_finalizer(*args, **kwargs))
        self.used = False
        self.entered = False
        self.start_time = None
        self.suppressed_exceptions = []
        self.suppress_all = False

    def __call__(self, *args, **kwargs):
        """
        Существуют 2 сценария вызова объекта LoggerRouteFinalizer как функции:
        1. При использовании роутера как фабрики декораторов. В этом случае сюда передается функция или класс. В этом случае управление передается методу self.rewrite_fields().
        2. Внутри контекста под контекстным менеджером. В этом случае передаваемые сюда аргументы предназначены для корректирования записываемого лога.
        """
        if self.entered:
            return self.rewrite_fields(*args, **kwargs)

        if len(args) != 1 and len(kwargs) > 0:
            raise IncorrectUseOfTheDecoratorError()
        wrappable = args[0]

        if self.used:
            raise IncorrectUseOfTheDecoratorError()
        self.used = True

        self.finalizer.detach()

        if inspect.isclass(wrappable):
            decorator_factory = clog
        elif callable(wrappable):
            decorator_factory = flog
        else:
            raise IncorrectUseOfTheDecoratorError()

        decorator = decorator_factory(**(self.data))
        return decorator(wrappable)

    def __enter__(self):
        """
        Вход в контекстный менеджер.
        """
        if self.used:
            raise IncorrectUseOfTheContextManagerError()
        self.used = True

        if self.entered:
            raise IncorrectUseOfTheContextManagerError()
        self.entered = True

        self.finalizer.detach()

        self.start_time = time()
        self.data['time'] = datetime.now()

        return self

    def __exit__(self, exception_type, exception_value, traceback_instance):
        """
        Выход из контекстного менеджера.

        После заполнения всех нужных полей и записи лога, решается вопрос, поднимать ли дальше исключение (если оно возникло) или подавить его.
        """
        if exception_type is not None:
            self.data['exception_type'] = exception_type.__name__
            self.data['exception_message'] = str(exception_value)
            self.data['success'] = False
            self.data['traceback'] = self.settings['json_module'].dumps(traceback.format_tb(traceback_instance))
        else:
            self.data['success'] = True

        self.data['time_of_work'] = time() - self.start_time

        simple_handle_log(**(self.data))

        if exception_value is not None:
            if self.suppress_all:
                return True
            if self.suppressed_exceptions:
                if self.settings['suppress_exception_subclasses']:
                    if any(isinstance(exception_value, suppressed_exception) for suppressed_exception in self.suppressed_exceptions):
                        return True
                    return False
                else:
                    if any(exception_type is suppressed_exception for suppressed_exception in self.suppressed_exceptions):
                        return True
                    return False
            else:
                return self.settings['suppress_by_default']

    def __repr__(self):
        """
        Текстовое представление объекта для функции repr().
        """
        kwargs = ((key, str(value)) if not isinstance(value, str) else (key, f'"{value}"') for key, value in self.data.items())
        kwargs = ', '.join([f'{key}={value}' for key, value in kwargs])
        return f'{type(self).__name__}({kwargs})'

    def __str__(self):
        """
        Текстовое представление объекта для функции str().
        """
        return f"<A {repr(self)} object, don't use it!>"

    def convert_arguments_to_dict(self, *args, **kwargs):
        """
        В объект LoggerRouteFinalizer разными способами могут передаваться аргументы от пользователя.
        Среди этих аргументов может оказаться строка, переданная как первый позиционный аргумент. Она должны быть преобразована в именованное поле 'message'.
        Метод возвращает все полученные от клиента аргументы в виде словаря.
        """
        if len(args) > 1 or (len(args) == 1 and not isinstance(args[0], str)):
            raise IncorrectUseLoggerError()

        result = {**kwargs}

        if len(args) == 1:
            if 'message' in kwargs and args[0] != kwargs['message']:
                simple_handle_log._maybe_raise(IncorrectUseLoggerError, 'You have specified the message both as an ordinal argument to the decorator and as a named argument.')
            result['message'] = args[0]

        return result

    def rewrite_fields(self, *args, **kwargs):
        """
        Данный метод вызывается когда клиент вызывает объект LoggerRouteFinalizer внутри вызванного контекстного менеджера.
        Сюда могут быть переданы аргументы, которые добавятся в формируемый объект лога. При конфликте между ранее заполненными полями и новыми - новые побеждают.
        """
        new_data = self.convert_arguments_to_dict(*args, **kwargs)
        self.data.update(new_data)

    def suppress(self, *exceptions):
        """
        Метод позволяет определить исключения, которые будут подавляться внутри контекстного менеджера. Его вызов производит действие, похожее на @suppress из стандартной библиотеки (https://docs.python.org/3/library/contextlib.html#contextlib.suppress).

        Применяться это должно примерно так:

        >>> from polog import log
        >>>
        >>> with log('kek').suppress(ValueError):
        >>> .... raise ValueError

        В примере выше исключение ValueError будет подавляться, однако все остальные исключения - нет (однако в зависимости от значения настройки 'suppress_exception_subclasses' также могут подавляться субклассы переданных исключений).

        В метод можно передавать одно или несколько исключений. В случае, если он будет вызван без аргументов вообще, будут подавляться все исключения.
        """
        if not exceptions:
            self.suppress_all = True

        exceptions_to_use = []

        for exception in exceptions:
            if not inspect.isclass(exception) or not issubclass(exception, Exception):
                simple_handle_log._maybe_raise(ValueError, 'Only exceptions can be passed to the .suppress() method.')
            else:
                exceptions_to_use.append(exception)

        self.suppressed_exceptions.extend(exceptions_to_use)

        return self

    @staticmethod
    def create_finalizer(*args, **kwargs):
        """
        Здесь происходит создание объекта функции, который будет вызван в случае, если по контексту будет ясно, что функция log() вызвана для обычного ручного логирования.
        """
        def finalizer():
            simple_handle_log(*args, **kwargs)
        return finalizer
