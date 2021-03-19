import time
import inspect
import datetime
from functools import wraps
from polog.core.settings_store import SettingsStore
from polog.core.writer import Writer
from polog.core.levels import Levels
from polog.core.registering_functions import RegisteringFunctions
from polog.core.utils.not_none_to_dict import not_none_to_dict
from polog.core.utils.get_errors_level import get_errors_level
from polog.core.utils.exception_to_dict import exception_to_dict
from polog.utils.json_vars import json_vars, json_one_variable
from polog.core.utils.get_traceback import get_traceback, get_locals_from_traceback
from polog.errors import LoggedError, IncorrectUseOfTheDecoratorError
from polog.loggers.handle.message import message as _message


class FunctionLogger:
    """
    Экземпляры данного класса - декораторы, включающие автоматическое логирование для функций.
    """

    def __init__(self, settings=SettingsStore()):
        self.settings = settings

    def __call__(self, *args, message=None, level=1, errors_level=None, is_method=False):
        """
        Фабрика декораторов логирования для функций. Можно вызывать как со скобками, так и без.
        """
        def error_logger(func):
            # Если функция уже ранее была задекорирована, мы декорируем ее саму, а не ее в уже задекорированном виде.
            func, before_change_func = RegisteringFunctions().get_original(func), func
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                """
                Обертка для корутин, вызов обернутой функции происходит через await.
                """
                _message._clean_context()
                args_dict = self.get_base_args_dict(func, message)
                try:
                    start = time.time()
                    args_dict['time'] = datetime.datetime.now()
                    result = await func(*args, **kwargs)
                except Exception as e:
                    finish = time.time()
                    self.log_exception_info(e, finish, start, args_dict, errors_level, *args, **kwargs)
                    self.reraise_exception(e)
                finish = time.time()
                self.log_normal_info(result, finish, start, args_dict, level, *args, **kwargs)
                return result
            @wraps(func)
            def wrapper(*args, **kwargs):
                """
                Обертка для обычных функций.
                """
                _message._clean_context()
                args_dict = self.get_base_args_dict(func, message)
                try:
                    start = time.time()
                    args_dict['time'] = datetime.datetime.now()
                    result = func(*args, **kwargs)
                except Exception as e:
                    finish = time.time()
                    self.log_exception_info(e, finish, start, args_dict, errors_level, *args, **kwargs)
                    self.reraise_exception(e)
                finish = time.time()
                self.log_normal_info(result, finish, start, args_dict, level, *args, **kwargs)
                return result
            if inspect.iscoroutinefunction(func):
                result = async_wrapper
            else:
                result = wrapper
            # Проверяем, что функцию не запрещено декорировать. Если запрещено - возвращаем оригинал, иначе - какой-то из wrapper'ов.
            result = RegisteringFunctions().get_function_or_wrapper(func, before_change_func, wrapper, is_method)
            return result
        # Определяем, как вызван декоратор - как фабрика декораторов (т. е. без позиционных аргументов) или как непосредственный декоратор.
        if not len(args):
            return error_logger
        elif len(args) == 1 and callable(args[0]):
            return error_logger(args[0])
        raise IncorrectUseOfTheDecoratorError('You used the logging decorator incorrectly. Read the documentation.')

    def get_base_args_dict(self, func, message):
        """
        При каждом вызове функции с логирующим декоратором создается словарь с аргументами, которые будут переданы в очередь для обработчиков.
        В этой функции данный словарь инициализируется и заполняется значениями, которые уже известны еще до запуска задекорированной функции.
        """
        args_dict = {}
        args_dict['auto'] = True
        if message is not None:
            args_dict['message'] = str(message)
        self.get_arg(func, args_dict, '__module__')
        self.get_arg(func, args_dict, '__name__', key_name='function')
        return args_dict

    @staticmethod
    def get_arg(obj, args, arg_name, key_name=None):
        """
        Извлекаем какой-то атрибут объекта по имени, после чего используем то же самое имя в качестве ключа для словарика, где в качестве значения этот объект сохраним.
        Перед использованием в качестве ключа удаляем из него дандеры.
        Если в объекте атрибут с данным именем отсутствует, в словарь ничего сохранено не будет.

        Аргументы:

        obj - исходный объект, из которого извлекаются данные.
        args - словарь, куда мы сохраняем данные.
        arg_name - строка с названием атрибута, который мы извлекаем.
        key_name (опционально) - ключ для сохранения извлеченного из obj атрибута в словаре args. Если данный параметр не задать, используется arg_name без дандеров.
        """
        if key_name is None:
            key_name = arg_name.replace('_', '')
        arg = getattr(obj, arg_name, None)
        not_none_to_dict(args, key_name, arg)

    def reraise_exception(self, exc):
        """
        Здесь решается, какое исключение поднять - оригинальное или встроенное в Polog, в зависимости от настроек.
        """
        if self.settings.original_exceptions:
            raise exc
        raise LoggedError(str(exc)) from exc

    def log_exception_info(self, exc, finish, start, args_dict, errors_level, *args, **kwargs):
        """
        Здесь происходит заполнение автоматически извлекаемых полей в случае исключения.
        В т. ч. извлекается вся информация об исключении - название, сообщение и т. д.
        """
        exc_type = type(exc)
        if not (exc_type is LoggedError):
            errors_level = get_errors_level(errors_level)
            if errors_level >= self.settings.level:
                exception_to_dict(args_dict, exc)
                args_dict['success'] = False
                args_dict['traceback'] = get_traceback()
                args_dict['local_variables'] = get_locals_from_traceback()
                args_dict['time_of_work'] = finish - start
                args_dict['level'] = errors_level
                input_variables = json_vars(*args, **kwargs)
                _message._copy_context(args_dict)
                if not (input_variables is None):
                    args_dict['input_variables'] = input_variables
                self.extract_extra_fields((args, kwargs), args_dict)
                Writer().write((args, kwargs), **args_dict)

    def log_normal_info(self, result, finish, start, args_dict, level, *args, **kwargs):
        """
        Заполнение автоматических полей в случае, когда исключения не было.
        """
        level = Levels.get(level)
        if level >= self.settings.level:
            args_dict['success'] = True
            args_dict['result'] = json_one_variable(result)
            args_dict['time_of_work'] = finish - start
            args_dict['level'] = level
            _message._copy_context(args_dict)
            input_variables = json_vars(*args, **kwargs)
            if not (input_variables is None):
                args_dict['input_variables'] = input_variables
            self.extract_extra_fields((args, kwargs), args_dict)
            Writer().write((args, kwargs), **args_dict)

    def extract_extra_fields(self, args, args_dict):
        """
        Здесь происходит извлечение данных для дополнительных полей.
        Если поле уже заполнено ранее, здесь оно не изменяется.
        """
        extra_fields = self.settings.extra_fields
        for name, field in extra_fields.items():
            if name not in args_dict:
                try:
                    value = field.get_data(args, **args_dict)
                    args_dict[name] = value
                except:
                    pass


flog = FunctionLogger()
